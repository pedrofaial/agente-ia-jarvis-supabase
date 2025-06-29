"""
Script de teste para verificar instalação do Redis
Execute: python test_redis.py
"""

import redis
import sys
import time

def test_redis_connection():
    """Testa a conexão com o Redis"""
    
    print("🔴 Testando conexão com Redis...\n")
    
    try:
        # Tentar conectar
        r = redis.Redis(
            host='localhost', 
            port=6379, 
            decode_responses=True,
            socket_connect_timeout=5
        )
        
        # Teste 1: Ping
        print("1️⃣ Teste de PING...")
        pong = r.ping()
        if pong:
            print("✅ Redis respondeu com PONG!\n")
        else:
            print("❌ Redis não respondeu ao PING\n")
            return False
        
        # Teste 2: Set/Get
        print("2️⃣ Teste de SET/GET...")
        r.set('teste_key', 'Olá Redis!')
        value = r.get('teste_key')
        if value == 'Olá Redis!':
            print(f"✅ Valor armazenado e recuperado: '{value}'\n")
        else:
            print("❌ Erro ao armazenar/recuperar valor\n")
            return False
        
        # Teste 3: Expiração
        print("3️⃣ Teste de expiração (TTL)...")
        r.setex('teste_ttl', 2, 'Valor temporário')
        ttl = r.ttl('teste_ttl')
        print(f"✅ Chave criada com TTL de {ttl} segundos")
        time.sleep(3)
        expired_value = r.get('teste_ttl')
        if expired_value is None:
            print("✅ Chave expirou corretamente!\n")
        else:
            print("❌ Chave não expirou\n")
        
        # Teste 4: Incremento
        print("4️⃣ Teste de incremento...")
        r.set('contador', 0)
        r.incr('contador')
        r.incr('contador')
        counter = r.get('contador')
        if counter == '2':
            print(f"✅ Contador incrementado para: {counter}\n")
        else:
            print("❌ Erro no incremento\n")
        
        # Teste 5: Listas
        print("5️⃣ Teste de listas...")
        r.delete('minha_lista')  # Limpar se existir
        r.rpush('minha_lista', 'item1', 'item2', 'item3')
        lista = r.lrange('minha_lista', 0, -1)
        if lista == ['item1', 'item2', 'item3']:
            print(f"✅ Lista criada: {lista}\n")
        else:
            print("❌ Erro ao criar lista\n")
        
        # Teste 6: Hash
        print("6️⃣ Teste de hash (objeto)...")
        r.hset('usuario:123', mapping={
            'nome': 'João',
            'email': 'joao@email.com',
            'idade': '30'
        })
        usuario = r.hgetall('usuario:123')
        print(f"✅ Hash criado: {usuario}\n")
        
        # Limpar dados de teste
        print("🧹 Limpando dados de teste...")
        r.delete('teste_key', 'contador', 'minha_lista', 'usuario:123')
        print("✅ Dados de teste removidos\n")
        
        # Informações do servidor
        print("📊 Informações do Redis:")
        info = r.info()
        print(f"- Versão: {info.get('redis_version', 'N/A')}")
        print(f"- Memória usada: {info.get('used_memory_human', 'N/A')}")
        print(f"- Clientes conectados: {info.get('connected_clients', 'N/A')}")
        print(f"- Uptime: {info.get('uptime_in_days', 'N/A')} dias")
        
        print("\n✅ ✅ ✅ Redis está funcionando perfeitamente! ✅ ✅ ✅")
        return True
        
    except redis.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao Redis!")
        print("\n📋 Verifique se:")
        print("1. O Redis está instalado")
        print("2. O serviço está rodando")
        print("3. A porta 6379 está livre")
        print("\n💡 Dicas:")
        print("- Windows: Use 'docker-compose up -d redis'")
        print("- Linux: Use 'sudo systemctl start redis-server'")
        print("- Docker: Use 'docker run -d -p 6379:6379 redis:alpine'")
        return False
        
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
        return False

def check_redis_installed():
    """Verifica se o Redis está instalado"""
    
    import subprocess
    import platform
    
    system = platform.system()
    
    try:
        if system == "Windows":
            # Verificar Docker
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
            if 'redis' in result.stdout:
                print("✅ Redis rodando via Docker")
                return True
        else:
            # Linux/Mac
            result = subprocess.run(['redis-cli', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Redis instalado: {result.stdout.strip()}")
                return True
    except:
        pass
    
    return False

if __name__ == "__main__":
    print("=" * 50)
    print("     TESTE DE INSTALAÇÃO DO REDIS")
    print("=" * 50)
    print()
    
    # Verificar instalação
    if not check_redis_installed():
        print("⚠️  Redis pode não estar instalado ou rodando")
        print("📖 Consulte: docs/REDIS_INSTALLATION_GUIDE.md")
        print()
    
    # Testar conexão
    success = test_redis_connection()
    
    print("\n" + "=" * 50)
    
    if not success:
        sys.exit(1)
