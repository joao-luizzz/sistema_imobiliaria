import hashlib
senha = "admin123"
hash_correto = hashlib.sha256(senha.encode()).hexdigest()
print(f"O hash correto para 'admin123' é:\n{hash_correto}")