FILE ?= ebpf-samples/linux/sockex1_kern.o
run: ebpf-samples
	pipenv run python3 -m disasm $(FILE)

ebpf-samples:
	git submodule update --recursive
