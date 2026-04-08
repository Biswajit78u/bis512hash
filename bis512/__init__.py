"""
BIS512 - Custom 512-bit Cryptographic Hash Function
Author: Biswajit Saha

A secure hash function designed for blockchain applications with:
- 512-bit output
- ASIC-resistant design
- Strong avalanche effect (49.7%)
- No collisions detected

Usage:
    from bis512 import hash_string, hash_bytes, hash_hex
    
    # Hash a string
    result = hash_string("Hello, World!")
    print(result)  # 128-character hex string
    
    # Hash bytes
    result = hash_bytes(b"Blockchain data")
    
    # Get hex from bytes
    hex_result = hash_hex(b"Any data")
"""

from .core import (
    hash_string,
    hash_bytes,
    hash_hex,
    hash,
    hexhash,
    byteshash,
    __version__
)

__all__ = [
    'hash_string',
    'hash_bytes', 
    'hash_hex',
    'hash',
    'hexhash',
    'byteshash',
    '__version__'
]

__author__ = "Biswajit Saha"
__version__ = "1.0.0"
__description__ = "Custom 512-bit cryptographic hash function for blockchain"
