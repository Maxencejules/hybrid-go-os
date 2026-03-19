package main

const keyedDigestMaxInput = 160

var sha256RoundConstants = [...]uint32{
	0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
	0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
	0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
	0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
	0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
	0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
	0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
	0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
	0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
	0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
	0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
	0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
	0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
	0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
	0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
	0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
}

func sha256RotateRight(v uint32, n uint32) uint32 {
	return (v >> n) | (v << (32 - n))
}

func sha256Compress(state *[8]uint32, block *[64]byte) {
	var w [64]uint32
	var idx int
	for idx = 0; idx < 16; idx++ {
		base := idx * 4
		w[idx] = uint32(block[base])<<24 |
			uint32(block[base+1])<<16 |
			uint32(block[base+2])<<8 |
			uint32(block[base+3])
	}
	for idx = 16; idx < 64; idx++ {
		s0 := sha256RotateRight(w[idx-15], 7) ^
			sha256RotateRight(w[idx-15], 18) ^
			(w[idx-15] >> 3)
		s1 := sha256RotateRight(w[idx-2], 17) ^
			sha256RotateRight(w[idx-2], 19) ^
			(w[idx-2] >> 10)
		w[idx] = w[idx-16] + s0 + w[idx-7] + s1
	}

	a := state[0]
	b := state[1]
	c := state[2]
	d := state[3]
	e := state[4]
	f := state[5]
	g := state[6]
	h := state[7]

	for idx = 0; idx < 64; idx++ {
		s1 := sha256RotateRight(e, 6) ^ sha256RotateRight(e, 11) ^ sha256RotateRight(e, 25)
		ch := (e & f) ^ ((^e) & g)
		temp1 := h + s1 + ch + sha256RoundConstants[idx] + w[idx]
		s0 := sha256RotateRight(a, 2) ^ sha256RotateRight(a, 13) ^ sha256RotateRight(a, 22)
		maj := (a & b) ^ (a & c) ^ (b & c)
		temp2 := s0 + maj

		h = g
		g = f
		f = e
		e = d + temp1
		d = c
		c = b
		b = a
		a = temp1 + temp2
	}

	state[0] += a
	state[1] += b
	state[2] += c
	state[3] += d
	state[4] += e
	state[5] += f
	state[6] += g
	state[7] += h
}

func sha256Digest(data []byte) [32]byte {
	state := [8]uint32{
		0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
		0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
	}

	var offset int
	for offset+64 <= len(data) {
		var block [64]byte
		copyBlock(&block, data[offset:offset+64])
		sha256Compress(&state, &block)
		offset += 64
	}

	var block [64]byte
	rem := len(data) - offset
	if rem > 0 {
		copyBlockPrefix(&block, data[offset:], rem)
	}
	block[rem] = 0x80
	if rem >= 56 {
		sha256Compress(&state, &block)
		clearBlock(&block)
	}

	bitLen := uint64(len(data)) * 8
	block[56] = byte(bitLen >> 56)
	block[57] = byte(bitLen >> 48)
	block[58] = byte(bitLen >> 40)
	block[59] = byte(bitLen >> 32)
	block[60] = byte(bitLen >> 24)
	block[61] = byte(bitLen >> 16)
	block[62] = byte(bitLen >> 8)
	block[63] = byte(bitLen)
	sha256Compress(&state, &block)

	var out [32]byte
	for idx := 0; idx < 8; idx++ {
		base := idx * 4
		out[base] = byte(state[idx] >> 24)
		out[base+1] = byte(state[idx] >> 16)
		out[base+2] = byte(state[idx] >> 8)
		out[base+3] = byte(state[idx])
	}
	return out
}

func keyedSignature(key []byte, payload []byte) [32]byte {
	var buf [keyedDigestMaxInput]byte
	total := 0
	total += copyBytes(buf[total:], key)
	total += copyBytes(buf[total:], payload)
	if total > len(buf) {
		return [32]byte{}
	}
	return sha256Digest(buf[:total])
}

func keyedSignatureString(key []byte, payload string) [32]byte {
	var buf [keyedDigestMaxInput]byte
	total := 0
	total += copyBytes(buf[total:], key)
	total += copyStringBytes(buf[total:], payload)
	if total > len(buf) {
		return [32]byte{}
	}
	return sha256Digest(buf[:total])
}

func sha256DigestString(data string) [32]byte {
	var buf [keyedDigestMaxInput]byte
	n := copyStringBytes(buf[:], data)
	if n > len(buf) {
		return [32]byte{}
	}
	return sha256Digest(buf[:n])
}

func copyBytes(dst []byte, src []byte) int {
	limit := len(src)
	if limit > len(dst) {
		limit = len(dst)
	}
	for idx := 0; idx < limit; idx++ {
		dst[idx] = src[idx]
	}
	return limit
}

func copyStringBytes(dst []byte, src string) int {
	limit := len(src)
	if limit > len(dst) {
		limit = len(dst)
	}
	for idx := 0; idx < limit; idx++ {
		dst[idx] = src[idx]
	}
	return limit
}

func copyBlock(dst *[64]byte, src []byte) {
	for idx := 0; idx < 64; idx++ {
		dst[idx] = src[idx]
	}
}

func copyBlockPrefix(dst *[64]byte, src []byte, n int) {
	for idx := 0; idx < n; idx++ {
		dst[idx] = src[idx]
	}
}

func clearBlock(dst *[64]byte) {
	for idx := 0; idx < 64; idx++ {
		dst[idx] = 0
	}
}

func digestPrefix8(sum [32]byte) [8]byte {
	var out [8]byte
	for idx := 0; idx < len(out); idx++ {
		out[idx] = sum[idx]
	}
	return out
}

func digestEqual(left [32]byte, right [32]byte) bool {
	for idx := 0; idx < len(left); idx++ {
		if left[idx] != right[idx] {
			return false
		}
	}
	return true
}
