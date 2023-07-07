import secrets
import base64

# Generate two random bytes sequences
key_part1 = secrets.token_bytes(16)
key_part2 = secrets.token_bytes(16)

# Concatenate the two parts
secret_key = key_part1 + key_part2

# Perform URL-safe base64 encoding
encoded_key = base64.urlsafe_b64encode(secret_key)

# Split the encoded key into two parts
encoded_part1 = encoded_key[:len(encoded_key) // 2]
encoded_part2 = encoded_key[len(encoded_key) // 2:]

print(str(encoded_part1)+str(encoded_part2))
