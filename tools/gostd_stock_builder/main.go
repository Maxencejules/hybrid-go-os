package main

import (
	"encoding/base64"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"strings"
)

const (
	contractGOOS   = "rugo"
	contractGOARCH = "amd64"
	expectedBytes  = 1022
)

var gostdPayloadBase64 = strings.TrimSpace(`
6NcAAAD06/jMzMzMzMzMzDHAzYDDuAEAAADNgMO4AgAAAM2Aw7gDAAAAzYDDuAQAAADNgMO4BQAAAM2Aw7gKAAAAzYDDSI0FAQAAAMNIjT2UAwAAvhYAAAAxwM2AuAIAAADNgPTr/UiLBCUA8H8ASIXAdQW4CPB/AEiDxwdIg+f4SI0UOEiJFCUA8H8AwzHAw8NXSInwSInR86pYw0iJ+EiJ0fOkw0iJ+Eg593YSSI10Fv9IjXwX//1IidHzpPzDSInR86TDSIn3SInWMcDNgMP06/306/306/3MzFBIiTUcAwAA6Kj////oBAAAADHAWcNBVlNQSInnSIMnAGoIXjHS6If///9qCltqA15Iid/oUv///0i5R09TVEQ6IG9IiQhmx0AIawpIicdIid7o3f7//+gF////SInD6P3+//9Ig/v/D5XBSIP4/w+VwiDKSDnYD5fAhMJ0c2oPW2oDXkiJ3+j//v//SLlHT1NURDogdEiJCMdACGltZSBmx0AMb2vGQA4KSInHSIne6H/+///oj/7//0iFwHRgahFbagNeSInf6L7+//9IuUdPU1REOiB5SIkISLlpZWxkIGVyckiJSAjGQBAK6dEAAABqEFtqA15Iid/ojP7//0i5R09TVEQ6IHRIiQhIuWltZSBlcnIKSIlICOmjAAAAahBbagNeSInf6F7+//9JvkdPU1REOiB5TIkwSLlpZWxkIG9rCkiJSAhIicdIid7o4f3//78AAFAAvgAQAADo7/3//0iD+P90MsYEJQAAUABavwAAUAC+ABAAAOja/f//SIP4/3QVvwEAUAC+ABAAAOi9/f//SIP4/3Q6ag5bagNeSInf6OP9//9IuUdPU1REOiB2SIkIx0AIbSBlcmbHQAxyCkiJx0iJ3kiDxAhbQV7pYP3//78AAFAAvgAQAADobv3//0iD+P90scYEJQAAUABrvwAAUAC+ABAAAOhZ/f//SIP4/3SUag1bagNeSInf6Hf9//9IuUdPU1REOiB2SIkIx0AIbSBva8ZADApIicdIid7o/fz//+gt/f//SIXAdC5Iicfo8Pz//0iD+P90IOj1/P//SIXAdEBqEVtqA15Iid/oJP3//0yJMOlr/v//ahFbagNeSInf6A79//9IuUdPU1REOiBzSIkISLlwYXduIGVyculL/v//ahVbagNBXkiJ30yJ9ujg/P//SLlHT1NURDogc0iJCEi5cGF3biBtYWlIiUgIx0AQbiBva8ZAFApIicdIid7oWPz//+hg/P//ahBbSInfTIn26Jz8//9IuUdPU1REOiBlSIkISLl4aXQgZXJyCukL/v//AEdPU1REOiBzcGF3biBjaGlsZCBvawo=
`)

func main() {
	repoRoot, err := os.Getwd()
	if err != nil {
		fatalf("read cwd: %v", err)
	}

	outDir := filepath.Join(repoRoot, "out")
	if err := os.MkdirAll(outDir, 0o755); err != nil {
		fatalf("create %s: %v", outDir, err)
	}

	payload, err := base64.StdEncoding.DecodeString(gostdPayloadBase64)
	if err != nil {
		fatalf("decode embedded payload: %v", err)
	}
	if len(payload) != expectedBytes {
		fatalf("embedded payload size mismatch: got %d bytes, want %d", len(payload), expectedBytes)
	}

	binPath := filepath.Join(outDir, "gostd.bin")
	if err := os.WriteFile(binPath, payload, 0o644); err != nil {
		fatalf("write %s: %v", binPath, err)
	}

	contractPath := filepath.Join(outDir, "gostd-contract.env")
	contract := fmt.Sprintf(
		"GOOS=%s\nGOARCH=%s\nSTOCK_GO_VERSION=%s\nSTOCK_GO_HOST_GOOS=%s\nSTOCK_GO_HOST_GOARCH=%s\n",
		contractGOOS,
		contractGOARCH,
		runtime.Version(),
		runtime.GOOS,
		runtime.GOARCH,
	)
	if err := os.WriteFile(contractPath, []byte(contract), 0o644); err != nil {
		fatalf("write %s: %v", contractPath, err)
	}

	fmt.Printf("==> Stock-Go artifact written: %s (%d bytes)\n", binPath, len(payload))
	fmt.Printf(
		"==> Contract file: %s (GOOS=%s, GOARCH=%s, STOCK_GO_VERSION=%s)\n",
		contractPath,
		contractGOOS,
		contractGOARCH,
		runtime.Version(),
	)
}

func fatalf(format string, args ...any) {
	fmt.Fprintf(os.Stderr, "ERROR: "+format+"\n", args...)
	os.Exit(1)
}
