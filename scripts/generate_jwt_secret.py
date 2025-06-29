# Script para gerar JWT_SECRET seguro
# Execute este script Python para gerar uma chave segura

import secrets
import string
import base64

def generate_jwt_secret():
    """Gera um JWT_SECRET criptograficamente seguro"""
    
    print("🔐 Gerando JWT_SECRET seguro...\n")
    
    # Método 1: Hexadecimal (64 caracteres)
    hex_secret = secrets.token_hex(32)
    print("1️⃣ Método Hexadecimal (Recomendado):")
    print(f"   {hex_secret}")
    print(f"   Tamanho: {len(hex_secret)} caracteres\n")
    
    # Método 2: URL-Safe Base64 (43 caracteres)
    urlsafe_secret = secrets.token_urlsafe(32)
    print("2️⃣ Método URL-Safe Base64:")
    print(f"   {urlsafe_secret}")
    print(f"   Tamanho: {len(urlsafe_secret)} caracteres\n")
    
    # Método 3: Alfanumérico customizado (64 caracteres)
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    custom_secret = ''.join(secrets.choice(alphabet) for _ in range(64))
    print("3️⃣ Método Alfanumérico + Símbolos:")
    print(f"   {custom_secret}")
    print(f"   Tamanho: {len(custom_secret)} caracteres\n")
    
    # Método 4: Bytes aleatórios em Base64 (44 caracteres)
    random_bytes = secrets.token_bytes(32)
    b64_secret = base64.b64encode(random_bytes).decode('utf-8')
    print("4️⃣ Método Base64 de Bytes Aleatórios:")
    print(f"   {b64_secret}")
    print(f"   Tamanho: {len(b64_secret)} caracteres\n")
    
    print("=" * 60)
    print("📌 RECOMENDAÇÃO: Use o Método 1 (Hexadecimal)")
    print("=" * 60)
    
    return hex_secret

if __name__ == "__main__":
    # Gera o secret
    recommended_secret = generate_jwt_secret()
    
    print("\n✅ Para usar no seu .env, copie esta linha:")
    print(f"\nJWT_SECRET={recommended_secret}")
    
    print("\n⚠️  IMPORTANTE:")
    print("- NUNCA commite este valor no Git")
    print("- Use um valor diferente em produção")
    print("- Guarde em um gerenciador de senhas seguro")
    print("- Se vazar, gere um novo imediatamente")
