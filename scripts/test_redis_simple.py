"""
Script de teste para verificar instalação do Redis
Execute: python test_redis_simple.py
"""

import redis
import sys
import time

def test_redis_connection():
    """Testa a conexão com o Redis"""
    
    print("Testando conexão com Redis...\n")
    
    try:
        # Tentar conectar
        r = redis.Redis(
            host='localhost', 
            port=6379, 
            decode_responses=True,
            socket_connect_timeout=5
        )
        
        # Teste 1: Ping
        print("[1] Teste de PING...")
        pong = r.ping()
        if pong:
            print("OK - Redis respondeu com PONG!\n")
        else:
            print("ERRO - Redis não respondeu ao PING\n")
            return False
        
        # Teste 2: Set/Get
        print("[2] Teste de SET/GET...")
        r.set('teste_key', 'Olá Redis!')
        value = r.get('teste_key')
        if value == 'Olá Redis!':
            print(f"OK - Valor armazenado e recuperado: '{value}'\n")
        else:
            print("ERRO - Erro ao armazenar/recuperar valor\n")
            return False
        
        # Teste 3: Expiração
        print("[3] Teste de expiração (TTL)...")
        r.setex('teste_ttl', 2, 'Valor temporário')
        ttl = r.ttl('teste_ttl')
        print(f"OK - Chave criada com TTL de {ttl} segundos")
        time.sleep(3)
        expired_value = r.get('teste_ttl')
        if expired_value is None:
            print("OK - Chave expirou corretamente!\n")
        else:
            print("ERRO - Chave não expirou\n")
        
        # Teste 4: Incremento
        print("[4] Teste de incremento...")
        r.set('contador', 0)
        r.incr('contador')
        r.incr('contador')
        counter = r.get('contador')
        if counter == '2':
            print(f"OK - Contador incrementado para: {counter}\n")
        else:
            print("ERRO - Erro no incremento\n")
        
        # Teste 5: Listas
        print("[5] Teste de listas...")
        r.delete('minha_lista')  # Limpar se existir
        r.rpush('minha_lista', 'item1', 'item2', 'item3')
        lista = r.lrange('minha_lista', 0, -1)
        if lista == ['item1', 'item2', 'item3']:
            print(f"OK - Lista criada: {lista}\n")
        else:
            print("ERRO - Erro ao criar lista\n")
        
        # Teste 6: Hash
        print("[6] Teste de hash (objeto)...")
        r.hset('usuario:123', mapping={
            'nome': 'João',
            'email': 'joao@email.com',
            'idade': '30'
        })
        usuario = r.hgetall('usuario:123')
        print(f"OK - Hash criado: {usuario}\n")
        
        # Limpar dados de teste
        print("Limpando dados de teste...")
        r.delete('teste_key', 'contador', 'minha_lista', 'usuario:123')
        print("OK - Dados de teste removidos\n")
        
        # Informações do servidor
        print("=== Informações do Redis ===")
        info = r.info()
        print(f"- Versão: {info.get('redis_version', 'N/A')}")
        print(f"- Memória usada: {info.get('used_memory_human', 'N/A')}")
        print(f"- Clientes conectados: {info.get('connected_clients', 'N/A')}")
        print(f"- Uptime: {info.get('uptime_in_days', 'N/A')} dias")
        
        print("\n*** SUCESSO: Redis está funcionando perfeitamente! ***")
        return True
        
    except redis.ConnectionError:
        print("ERRO: Não foi possível conectar ao Redis!")
        print("\nVerifique se:")
        print("1. O Redis está instalado")
        print("2. O serviço está rodando")
        print("3. A porta 6379 está livre")
        print("\nDicas:")
        print("- Windows: Use 'docker-compose up -d redis'")
        print("- Linux: Use 'sudo systemctl start redis-server'")
        print("- Docker: Use 'docker run -d -p 6379:6379 redis:alpine'")
        return False
        
    except Exception as e:
        print(f"ERRO inesperado: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("     TESTE DE INSTALAÇÃO DO REDIS")
    print("=" * 50)
    print()
    
    # Testar conexão
    success = test_redis_connection()
    
    print("\n" + "=" * 50)
    
    if not success:
        sys.exit(1)
