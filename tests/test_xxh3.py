import xxh3
import io
import subprocess
import random
import os

def test_random():
    for _ in range(100):
        print('.', end='', flush=True)
        data = os.urandom(int(random.random() * int(10 * 1024 * 1024))) # Read 1mb
        with open('/tmp/test.data', 'wb') as f:
            f.write(data)

        expected = subprocess.check_output('cat /tmp/test.data | xxh3', shell=True).decode('utf-8').strip() # github.com/nathants/bsv
        assert xxh3.stream_hex(io.BytesIO(data)) == expected
        with open('/tmp/test.data', 'rb') as f:
            assert xxh3.stream_hex(f) == expected

        expected = subprocess.check_output('cat /tmp/test.data | xxh3 --int', shell=True).decode('utf-8').strip() # github.com/nathants/bsv
        expected = int(expected)
        assert xxh3.stream_int(io.BytesIO(data)) == expected
        with open('/tmp/test.data', 'rb') as f:
            assert xxh3.stream_int(f) == expected

        data = data[:1024]
        with open('/tmp/test.data', 'wb') as f:
            f.write(data)
        expected = subprocess.check_output('cat /tmp/test.data | xxh3', shell=True).decode('utf-8').strip() # github.com/nathants/bsv
        assert xxh3.stream_hex(io.BytesIO(data)) == expected
        assert xxh3.oneshot_hex(data) == expected

        data = data[:1024]
        with open('/tmp/test.data', 'wb') as f:
            f.write(data)
        expected = subprocess.check_output('cat /tmp/test.data | xxh3 --int', shell=True).decode('utf-8').strip() # github.com/nathants/bsv
        expected = int(expected)
        assert xxh3.stream_int(io.BytesIO(data)) == expected
        assert xxh3.oneshot_int(data) == expected
