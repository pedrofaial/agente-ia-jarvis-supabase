import secrets

# Gera um JWT_SECRET seguro de 64 caracteres hexadecimais
jwt_secret = secrets.token_hex(32)

print("JWT_SECRET Gerado com Sucesso!")
print("=" * 70)
print(jwt_secret)
print("=" * 70)
print("\nCopie a linha abaixo para o seu arquivo .env:")
print(f"\nJWT_SECRET={jwt_secret}")
print("\nIMPORTANTE: NUNCA compartilhe esta chave!")
