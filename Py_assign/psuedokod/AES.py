CLASS KeyExchange
    PROCEDURE __init__(g = 5, p = 97)
        self.g
        self.p
        self.private ← RANDOM_INTEGER(1, 50)
        self.public ← (g ^ self.private) mod p
    END PROCEDURE

    FUNCTION generate_shared_key(other_public)
        shared_secret ← (other_public ^ self.private) mod self.p
        RETURN SHA-256( STRING(shared_secret) )
    END FUNCTION
END CLASS

FUNCTION pseudo_encrypt(plaintext, key, rounds = 3)
    data ← BYTES(plaintext)

    FOR r ← 0 TO rounds − 1 DO
        FOR i ← 0 TO LENGTH(data) − 1 DO
            byte ← data[i]
            k_byte ← key[(i + r) mod LENGTH(key)]
            pos_mask ← ((i + r) * 13) mod 256
            data[i] ← byte XOR k_byte XOR pos_mask
        END FOR
    END FOR

    RETURN BASE64_ENCODE(data)
END FUNCTION

FUNCTION pseudo_decrypt(ciphertext, key, rounds = 3)
    data ← BASE64_DECODE(ciphertext)

    FOR r ← rounds − 1 DOWNTO 0 DO
        FOR i ← 0 TO LENGTH(data) − 1 DO
            byte ← data[i]
            pos_mask ← ((i + r) * 13) mod 256
            k_byte ← key[(i + r) mod LENGTH(key)]
            data[i] ← byte XOR pos_mask XOR k_byte
        END FOR
    END FOR

    RETURN STRING(data)
END FUNCTION
