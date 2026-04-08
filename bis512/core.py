"""
BIS512 - Pure Python Implementation
Author: Biswajit Saha

Custom 512-bit cryptographic hash function
Works on any platform without C compiler
"""

import struct
import sys

BLOCK_BYTES = 64
EXPANDED_WORDS = 64
ROUNDS = 10

# Constants array
ARR = [
    0x10E9B6DB, 0x1950C8E8, 0x2A2F9833, 0x3B14F61F, 0x213F2F55, 0x321B4A70, 0x1842A0A7, 0x2926B4C2,
    0x0F4B2A78, 0x0654C2CA, 0x1735A765, 0x0E3E8AB7, 0x3000E1ED, 0x0546F7A8, 0x2708B1DE, 0x1E114510,
    0x1519D9E1, 0x25FA6A7C, 0x1D0312CE, 0x0329F284, 0x140B8E9F, 0x0B13C771, 0x2CD77C27, 0x23D92AF9,
    0x2BC7E4DE, 0x11F0B0F4, 0x22CFEF1F, 0x08F8C955, 0x19D8C8F0, 0x000ECF66, 0x3A9DFA79, 0x20C3F9AF,
    0x17CBE6E1, 0x28AC67DC, 0x05DC2FA4, 0x16BCA0BF, 0x0DC5E311, 0x04CEBBA3, 0x268EAC99, 0x1D9A3B6B,
    0x1492F73D, 0x257F7C58, 0x02B1B260, 0x1394B97B, 0x3556B7B1, 0x0A9B7F4C, 0x3445E8F0, 0x2257B713,
    0x087E6E79, 0x195B5A64, 0x3B1F61DA, 0x323A0E0C, 0x0771E6A7, 0x203D74AF, 0x1735E061, 0x0E4A52B3,
    0x0553C105, 0x163B1EA0, 0x0D3E5C72, 0x2F0E6D28, 0x04464FC3, 0x1D11C74B, 0x1C0E8CDE, 0x022A4E94
]

# Scattered positions for compression
POSITIONS = [
    0, 23, 45, 61, 3, 19, 38, 52, 7, 31, 49, 58, 11, 27, 43, 63,
    15, 34, 50, 5, 21, 39, 54, 9, 25, 41, 56, 13, 29, 47, 60, 2,
    17, 36, 51, 8, 24, 42, 57, 14, 30, 48, 62, 4, 20, 37, 53, 10,
    26, 44, 59, 1, 18, 35, 55, 12, 28, 46, 61, 6, 22, 40, 33, 16
]

def _popcount(x):
    """Count number of 1 bits in a 32-bit integer"""
    return bin(x & 0xFFFFFFFF).count('1')

def _count_zero_bits(x):
    return 32 - _popcount(x)

def _count_one_bits(x):
    return _popcount(x)

def _left_rotate(x, n):
    n = n % 32
    x = x & 0xFFFFFFFF
    return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF

def _right_rotate(x, n):
    n = n % 32
    x = x & 0xFFFFFFFF
    return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF

def _rlm(x):
    """Right rotate 10, Left rotate 10, then Majority bit selection"""
    r = _right_rotate(x, 10)
    l = _left_rotate(x, 10)
    return (r & l) | (l & x) | (x & r)

def _majority(x, y, z):
    """Majority function: output 1 if at least 2 bits are 1"""
    return (x & y) | (y & z) | (z & x)

def _xor_excluding_self(words):
    """XOR all words, then XOR each word with the total"""
    total = 0
    for w in words:
        total ^= w
    return [(total ^ w) & 0xFFFFFFFF for w in words]

def _expand_words(words):
    """Expand 16 words to 64 words using 4-word types"""
    out = words[:] + [0] * (64 - 16)
    for i in range(16, 64):
        w1 = out[i - 16]
        w2 = (~out[i - 12]) & 0xFFFFFFFF
        w3 = _rlm(out[i - 8])
        w4 = _left_rotate(out[i - 4], 7)
        out[i] = (w1 ^ w2 ^ w3 ^ w4) & 0xFFFFFFFF
    return out

def _compress_64_to_16(words):
    """Compress 64 words to 16 words using scattered positions and majority"""
    constants = []
    for i in range(16):
        a = words[i]
        b = words[i + 16]
        c = words[i + 32]
        d = words[i + 48]
        const = (_left_rotate(a, 7) ^ _right_rotate(b, 13) ^ 
                 _rlm(c) ^ ((d << 3) & 0xFFFFFFFF) ^ (d >> 5)) & 0xFFFFFFFF
        constants.append(const)
    
    result = []
    idx = 0
    for i in range(16):
        a = words[POSITIONS[idx]]; idx += 1
        b = words[POSITIONS[idx]]; idx += 1
        c = words[POSITIONS[idx]]; idx += 1
        d = words[POSITIONS[idx]]; idx += 1
        
        pair1 = ((a >> 7) ^ _left_rotate(b, 13)) & 0xFFFFFFFF
        pair2 = ((c << 5) ^ _right_rotate(d, 11)) & 0xFFFFFFFF
        
        pair1 ^= (1 << 7)
        pair2 = (~pair2) & 0xFFFFFFFF
        
        res = _majority(pair1, pair2, constants[15 - i])
        result.append(res & 0xFFFFFFFF)
    
    return result

def _pad_message(msg_bytes):
    """Pad message to multiple of 512 bits (SHA-style padding)"""
    msg_len = len(msg_bytes)
    msg_bits = msg_len * 8
    total_bits = msg_bits + 1 + 64
    total_bytes = ((total_bits + 511) // 512) * 64
    
    data = bytearray(total_bytes)
    data[:msg_len] = msg_bytes
    data[msg_len] = 0x80
    
    for i in range(8):
        data[total_bytes - 1 - i] = (msg_bits >> (8 * i)) & 0xFF
    
    return data

def _compute_hash_bytes(data: bytes) -> bytes:
    """Internal function - returns raw bytes hash (64 bytes)"""
    padded = _pad_message(data)
    block_count = len(padded) // BLOCK_BYTES
    
    H = [0] * 16
    
    for b in range(block_count):
        block = padded[b * BLOCK_BYTES:(b + 1) * BLOCK_BYTES]
        
        # Extract 16 words from block
        words = []
        for w in range(16):
            start = w * 4
            word = (block[start] << 24) | (block[start + 1] << 16) | \
                   (block[start + 2] << 8) | block[start + 3]
            words.append(word)
        
        # XOR excluding self
        xor_words = _xor_excluding_self(words)
        
        # Apply rotation based on even/odd indices
        rotated = []
        for w in range(16):
            if w % 2 == 0:
                zero_count = _count_zero_bits(xor_words[w])
                shift = 8 + (zero_count % 24)
                rotated.append(_left_rotate(xor_words[w], shift))
            else:
                one_count = _count_one_bits(xor_words[w])
                shift = 8 + (one_count % 24)
                rotated.append(_right_rotate(xor_words[w], shift))
        
        # XOR with constants from ARR
        for w in range(16):
            idx = ((rotated[w] >> 16) ^ (rotated[w] & 0xFFFF) ^ w) % 64
            rotated[w] ^= ARR[idx]
        
        current = rotated[:]
        
        # Perform multiple rounds of Expand → Compress
        for _ in range(ROUNDS):
            expanded = _expand_words(current)
            compressed = _compress_64_to_16(expanded)
            current = compressed[:]
        
        # Update final hash
        for i in range(16):
            H[i] ^= current[i]
    
    # Convert to bytes (big-endian)
    result = bytearray()
    for word in H:
        result.extend(struct.pack('>I', word))
    return bytes(result)


# ============== Public API ==============

def hash_bytes(data: bytes) -> bytes:
    """
    Hash bytes and return raw bytes (64 bytes)
    
    Args:
        data: Input bytes to hash
        
    Returns:
        64-byte hash value
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    return _compute_hash_bytes(data)


def hash_string(data: str) -> str:
    """
    Hash a string and return hex string (128 characters)
    
    Args:
        data: Input string to hash
        
    Returns:
        128-character hexadecimal hash
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    hash_bytes = _compute_hash_bytes(data)
    return hash_bytes.hex()


def hash_hex(data: bytes) -> str:
    """
    Hash bytes and return hex string (128 characters)
    
    Args:
        data: Input bytes to hash
        
    Returns:
        128-character hexadecimal hash
    """
    return _compute_hash_bytes(data).hex()


# Aliases for convenience
hash = hash_string
hexhash = hash_hex
byteshash = hash_bytes


# Version info
__version__ = "1.0.0"
__author__ = "Biswajit Saha"
