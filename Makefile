# Heliosphere Build System

.PHONY: all grn-1kw sim test clean

all: grn-1kw sim

grn-1kw:
	@echo "Building 1-kW GRN BOM..."
	@echo "Components:"
	@echo "- 10 m² rectenna film: $$500"
	@echo "- GaAs Schottky diodes: $$200"
	@echo "- DC-DC converter: $$150"
	@echo "Total: $$850"

# `make sim` used to run `python3 sim/beam_trace.py` with no arguments, and the
# script REQUIRES --ish_power and --distance. So the documented build command
# has never worked, and `make all` failed with it. The defaults below are the
# design point this repository's own documents state — 10 GW at the ISH
# (docs/README.md) beamed to a geostationary MOR at 35,786 km — and either can
# be overridden:  make sim ISH_POWER=2e9 DISTANCE=1.2e7
ISH_POWER ?= 1e10
DISTANCE   ?= 3.5786e7

sim:
	@echo "Running simulations (ISH_POWER=$(ISH_POWER) W, DISTANCE=$(DISTANCE) m)..."
	python3 sim/beam_trace.py --ish_power $(ISH_POWER) --distance $(DISTANCE)

test:
	@echo "Running simulator tests..."
	python3 -m unittest discover -s sim -p "test_*.py" -v

clean:
	@echo "Cleaning build artifacts..."
