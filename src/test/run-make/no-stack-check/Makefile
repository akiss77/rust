-include ../tools.mk

ifdef IS_WINDOWS
# On Windows we use __chkstk and it only appears in functions with large allocations,
# so this test wouldn't be reliable.
all:
else ifdef IS_AARCH64
all:
else
all:
	$(RUSTC) -O --emit asm attr.rs
	! grep -q morestack $(TMPDIR)/attr.s
	$(RUSTC) -O --emit asm flag.rs
	grep -q morestack $(TMPDIR)/flag.s
	$(RUSTC) -O --emit asm -C no-stack-check flag.rs
	! grep -q morestack $(TMPDIR)/flag.s
endif
