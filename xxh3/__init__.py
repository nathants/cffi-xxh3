from cffi import FFI
import io
import itertools

ffibuilder = FFI()

ffibuilder.cdef(r"""

extern "Python" size_t _py_fread(char* ptr, size_t size, size_t count, unsigned stream);
uint64_t _xxh3_stream_int(unsigned stream);
uint64_t _xxh3_int(unsigned stream, unsigned size);

""")

ffibuilder.set_source(
    "_xxh3_cffi",
    r'''
#include <assert.h>
#include "xxh3.h"

#define BUFFER_SIZE 1024
#define ASSERT(cond, ...) if (!(cond)) { fprintf(stderr, ##__VA_ARGS__); exit(1); }

static size_t _py_fread(char* ptr, size_t size, size_t count, unsigned stream);

uint64_t _xxh3_int(unsigned stream, unsigned size) {
    char buffer[size];
    size_t read_bytes = _py_fread(buffer, 1, size, stream);
    ASSERT(read_bytes == size, "didnt read enought bytes\n");
    return XXH3_64bits(buffer, size);
}

uint64_t _xxh3_stream_int(unsigned stream) {
    size_t read_bytes;
    XXH3_state_t state;
    char buffer[BUFFER_SIZE];
    ASSERT(XXH3_64bits_reset(&state) != XXH_ERROR, "xxh3 reset failed\n");
    while (1) {
        read_bytes = _py_fread(buffer, 1, BUFFER_SIZE, stream);
        ASSERT(XXH3_64bits_update(&state, buffer, read_bytes) != XXH_ERROR, "xxh3 update failed\n");
        if (BUFFER_SIZE != read_bytes)
            break;
    }
    return XXH3_64bits_digest(&state);
}

    ''',
    sources=['xxh3/xxhash.c'],
    include_dirs=['xxh3'],
    extra_compile_args=['-Wall', '-O3',  '-march=native', '-mtune=native'],
)

try:
    from _xxh3_cffi import ffi, lib
except:
    pass
else:
    read_i = itertools.count(0)
    read_streams = {}

    @ffi.def_extern()
    def _py_fread(ptr, size, count, stream):
        size *= count
        val = read_streams[stream].read(size)
        read_size = len(val)
        ffi.memmove(ptr, val, read_size)
        return read_size

    def oneshot_int(val):
        assert len(val) <= 1024, 'to hash large values use the streaming interface'
        in_file = next(read_i)
        read_streams[in_file] = io.BytesIO(val)
        val = lib._xxh3_int(in_file, len(val))
        del read_streams[in_file]
        return val

        return lib._xxh3_int(val, len(val))

    def oneshot_hex(val):
        return hex(oneshot_int(val))[2:].rjust(16, '0')

    def stream_int(reader):
        in_file = next(read_i)
        read_streams[in_file] = reader
        val = lib._xxh3_stream_int(in_file)
        del read_streams[in_file]
        return val

    def stream_hex(reader):
        return hex(stream_int(reader))[2:].rjust(16, '0')

if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
