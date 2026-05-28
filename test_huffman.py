import os
import tempfile
import unittest

from huffman import compress_file, compress_text, decompress_file, decompress_text


class HuffmanTests(unittest.TestCase):
    def test_text_round_trip(self):
        original = "Food - Rs. 1200\nTravel - Rs. 800\nShopping - Rs. 2500\n"
        compressed, codes, padding = compress_text(original)
        restored = decompress_text(compressed, codes, padding)
        self.assertEqual(restored, original)

    def test_file_round_trip(self):
        with tempfile.TemporaryDirectory() as folder:
            input_path = os.path.join(folder, "report.txt")
            compressed_path = os.path.join(folder, "report.bin")
            output_path = os.path.join(folder, "restored.txt")

            with open(input_path, "w", encoding="utf-8") as file:
                file.write("Salary - Rs. 50000\nBills - Rs. 4200\n")

            result = compress_file(input_path, compressed_path)
            decompress_file(compressed_path, output_path)

            with open(output_path, "r", encoding="utf-8") as file:
                self.assertEqual(file.read(), "Salary - Rs. 50000\nBills - Rs. 4200\n")
            self.assertIn("compression_ratio", result)


if __name__ == "__main__":
    unittest.main()
