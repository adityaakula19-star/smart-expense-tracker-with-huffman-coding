import heapq
import json
import os
from collections import Counter
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(order=True)
class _HeapNode:
    frequency: int
    order: int
    char: Optional[str] = None
    left: Optional["_HeapNode"] = None
    right: Optional["_HeapNode"] = None


def _build_tree(text: str) -> Optional[_HeapNode]:
    frequency = Counter(text)
    heap = []

    for order, (char, count) in enumerate(frequency.items()):
        heapq.heappush(heap, _HeapNode(count, order, char))

    if not heap:
        return None

    order = len(heap)
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = _HeapNode(left.frequency + right.frequency, order, None, left, right)
        heapq.heappush(heap, merged)
        order += 1

    return heap[0]


def _generate_codes(node: Optional[_HeapNode], prefix: str = "", codes: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    if codes is None:
        codes = {}

    if node is None:
        return codes

    if node.char is not None:
        codes[node.char] = prefix or "0"
        return codes

    _generate_codes(node.left, prefix + "0", codes)
    _generate_codes(node.right, prefix + "1", codes)
    return codes


def compress_text(text: str) -> tuple[bytes, Dict[str, str], int]:
    """Return packed bytes, Huffman codes, and padding bit count."""
    if not text:
        return b"", {}, 0

    tree = _build_tree(text)
    codes = _generate_codes(tree)
    encoded = "".join(codes[char] for char in text)
    padding = (8 - len(encoded) % 8) % 8
    encoded += "0" * padding

    compressed = bytearray()
    for index in range(0, len(encoded), 8):
        compressed.append(int(encoded[index:index + 8], 2))

    return bytes(compressed), codes, padding


def decompress_text(data: bytes, codes: Dict[str, str], padding: int) -> str:
    if not data:
        return ""

    reverse_codes = {code: char for char, code in codes.items()}
    bit_string = "".join(format(byte, "08b") for byte in data)
    if padding:
        bit_string = bit_string[:-padding]

    result = []
    current = ""
    for bit in bit_string:
        current += bit
        if current in reverse_codes:
            result.append(reverse_codes[current])
            current = ""

    if current:
        raise ValueError("Compressed data is incomplete or corrupted.")

    return "".join(result)


def compress_file(input_path: str, output_path: str) -> dict:
    with open(input_path, "r", encoding="utf-8") as file:
        text = file.read()

    compressed, codes, padding = compress_text(text)
    metadata = {
        "codes": codes,
        "padding": padding,
        "original_extension": os.path.splitext(input_path)[1],
    }
    metadata_bytes = json.dumps(metadata, ensure_ascii=False).encode("utf-8")

    with open(output_path, "wb") as file:
        file.write(len(metadata_bytes).to_bytes(4, "big"))
        file.write(metadata_bytes)
        file.write(compressed)

    original_size = os.path.getsize(input_path)
    compressed_size = os.path.getsize(output_path)
    ratio = 0 if original_size == 0 else round((1 - compressed_size / original_size) * 100, 2)

    return {
        "original_size": original_size,
        "compressed_size": compressed_size,
        "compression_ratio": ratio,
    }


def decompress_file(input_path: str, output_path: str) -> None:
    with open(input_path, "rb") as file:
        metadata_length = int.from_bytes(file.read(4), "big")
        metadata = json.loads(file.read(metadata_length).decode("utf-8"))
        compressed = file.read()

    text = decompress_text(compressed, metadata["codes"], metadata["padding"])
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(text)
