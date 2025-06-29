-- Functions otimizadas para análises comuns
-- Evitam processamento linha por linha, retornam dados agregados

-- 1. Dashboard Resumo da Obra
CREATE OR REPLACE FUNCTION get_obra_dashboard(p_obra_id UUID, p_user_id UUID)
RETURNS JSON AS $$
BEGIN
  RETURN json_build_object(
    'info_basica', (
      SELECT json_build_object(
        'nome', nome,
        'cliente', cliente,
        'status', status,
        'progresso', COALESCE(
          ROUND((data_inicio::date - CURRENT_DATE) * 100.0 / 
          NULLIF(data_termino::date - data_inicio::date, 0)), 0
        ),
        'dias_restantes', data_termino::date - CURRENT_DATE
      )
      FROM obras 
      WHERE id = p_obra_id AND user_id = p_user_id
    ),
    'financeiro', (
      SELECT json_build_object(
        'orcamento_total', COALESCE(SUM(valor_total_orcado), 0),
        'gasto_total', COALESCE((
          SELECT SUM(valor) 
          FROM lancamentos_financeiros 
          WHERE obra_id = p_obra_id AND user_id = p_user_id
        ), 0),
        'saldo', COALESCE(SUM(valor_total_orcado), 0) - COALESCE((
          SELECT SUM(valor) 
          FROM lancamentos_financeiros 
          WHERE obra_id = p_obra_id AND user_id = p_user_id
        ), 0)
      )
      FROM itens_orcamento
      WHERE obra_id = p_obra_id AND user_id = p_user_id
    ),
    'alertas', (
      SELECT json_agg(alerta)
      FROM (
        -- Pagamentos vencidos
        SELECT json_build_object(
          'tipo', 'pagamento_vencido',
          'mensagem', CONCAT('Pagamento vencido: ', descricao),
          'valor', valor,
          'dias_atraso', CURRENT_DATE - data_vencimento::date
        ) as alerta
        FROM lancamentos_financeiros
        WHERE obra_id = p_obra_id 
          AND user_id = p_user_id
          AND status = 'pendente'
          AND data_vencimento < CURRENT_DATE
        LIMIT 5
      ) alertas
    )
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. Análise de Fornecedores
CREATE OR REPLACE FUNCTION get_fornecedores_analytics(p_user_id UUID, p_periodo_meses INT DEFAULT 3)
RETURNS JSON AS $$
BEGIN
  RETURN json_build_object(
    'top_fornecedores', (
      SELECT json_agg(
        json_build_object(
          'nome', f.nome,
          'total_gasto', COALESCE(SUM(l.valor), 0),
          'num_transacoes', COUNT(l.id),
          'ticket_medio', COALESCE(AVG(l.valor), 0)
        )
        ORDER BY SUM(l.valor) DESC
      )
      FROM fornecedores f
      LEFT JOIN lancamentos_financeiros l ON f.id = l.fornecedor_id
      WHERE f.user_id = p_user_id
        AND l.created_at >= CURRENT_DATE - INTERVAL '1 month' * p_periodo_meses
      GROUP BY f.id, f.nome
      LIMIT 10
    ),
    'resumo_periodo', (
      SELECT json_build_object(
        'total_fornecedores', COUNT(DISTINCT fornecedor_id),
        'total_transacoes', COUNT(*),
        'valor_total', COALESCE(SUM(valor), 0)
      )
      FROM lancamentos_financeiros
      WHERE user_id = p_user_id
        AND created_at >= CURRENT_DATE - INTERVAL '1 month' * p_periodo_meses
    )
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. Fluxo de Caixa Mensal
CREATE OR REPLACE FUNCTION get_fluxo_caixa(p_user_id UUID, p_obra_id UUID DEFAULT NULL)
RETURNS JSON AS $$
BEGIN
  RETURN (
    SELECT json_agg(
      json_build_object(
        'mes', TO_CHAR(date_trunc('month', data_emissao), 'YYYY-MM'),
        'entradas', 0, -- Futura implementação
        'saidas', COALESCE(SUM(CASE WHEN valor < 0 THEN ABS(valor) ELSE valor END), 0),
        'num_lancamentos', COUNT(*)
      )
      ORDER BY date_trunc('month', data_emissao)
    )
    FROM lancamentos_financeiros
    WHERE user_id = p_user_id
      AND (p_obra_id IS NULL OR obra_id = p_obra_id)
      AND data_emissao >= CURRENT_DATE - INTERVAL '12 months'
    GROUP BY date_trunc('month', data_emissao)
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 4. Comparação entre Obras
CREATE OR REPLACE FUNCTION compare_obras(p_user_id UUID, p_obra_ids UUID[])
RETURNS JSON AS $$
BEGIN
  RETURN (
    SELECT json_agg(
      json_build_object(
        'obra_id', o.id,
        'nome', o.nome,
        'orcamento', COALESCE(orcamento.total, 0),
        'gasto', COALESCE(gastos.total, 0),
        'eficiencia', CASE 
          WHEN COALESCE(orcamento.total, 0) > 0 
          THEN ROUND((COALESCE(gastos.total, 0) / orcamento.total) * 100, 2)
          ELSE 0 
        END,
        'dias_projeto', COALESCE(o.data_termino::date - o.data_inicio::date, 0),
        'status', o.status
      )
    )
    FROM obras o
    LEFT JOIN (
      SELECT obra_id, SUM(valor_total_orcado) as total
      FROM itens_orcamento
      GROUP BY obra_id
    ) orcamento ON o.id = orcamento.obra_id
    LEFT JOIN (
      SELECT obra_id, SUM(valor) as total
      FROM lancamentos_financeiros
      GROUP BY obra_id
    ) gastos ON o.id = gastos.obra_id
    WHERE o.user_id = p_user_id
      AND o.id = ANY(p_obra_ids)
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 5. Busca Inteligente
CREATE OR REPLACE FUNCTION search_all(p_user_id UUID, p_query TEXT)
RETURNS JSON AS $$
BEGIN
  RETURN json_build_object(
    'obras', (
      SELECT json_agg(row_to_json(o))
      FROM obras o
      WHERE user_id = p_user_id
        AND (
          nome ILIKE '%' || p_query || '%' OR
          cliente ILIKE '%' || p_query || '%' OR
          endereco ILIKE '%' || p_query || '%'
        )
      LIMIT 5
    ),
    'fornecedores', (
      SELECT json_agg(row_to_json(f))
      FROM fornecedores f
      WHERE user_id = p_user_id
        AND (
          nome ILIKE '%' || p_query || '%' OR
          cnpj ILIKE '%' || p_query || '%' OR
          email ILIKE '%' || p_query || '%'
        )
      LIMIT 5
    ),
    'lancamentos', (
      SELECT json_agg(row_to_json(l))
      FROM lancamentos_financeiros l
      WHERE user_id = p_user_id
        AND (
          descricao ILIKE '%' || p_query || '%' OR
          numero_documento ILIKE '%' || p_query || '%'
        )
      LIMIT 5
    )
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
