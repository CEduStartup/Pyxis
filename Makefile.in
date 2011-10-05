.DEFAULT_GOAL := all

ADMINGUI_DIR := admingui
COLLECTOR_DIR := collector
GRAPHGUI_DIR := graphgui
LOGGER_DIR := logger

PIP_REQUIRE := requirements.txt

TARGETS := all collector-all admingui-all graphgui-all collector admingui graphgui logger

.PHONY: $(TARGETS)

all: collector admingui graphgui logger
	@echo Making $@ done.

collector-all: collector logger
	@echo Making $@ done.

admingui-all: admingui logger
	@echo Making $@ done.

graphgui-all: graphgui logger
	@echo Making $@ done.

collector:
	@echo Making $@.
	pip install -r $(COLLECTOR_DIR)/$(PIP_REQUIRE)
	@echo Making $@ done.

admingui:
	@echo Making $@.
	pip install -r $(ADMINGUI_DIR)/$(PIP_REQUIRE)
	@echo Making $@ done.

graphgui:
	@echo Making $@.
	pip install -r $(GRAPHGUI_DIR)/$(PIP_REQUIRE)
	@echo Making $@ done.

logger:
	@echo Making $@.
	pip install -r $(LOGGER_DIR)/$(PIP_REQUIRE)
	@echo Making $@ done.

$(TARGETS): pre_clean create_run_script

pre_clean:
	@echo Pre-make cleaning.
	-rm run.sh

create_run_script: pre_clean
	@echo Creating executable run script.
	touch run.sh
	chmod +x run.sh

post_write_runscript: $(TARGETS)
	@echo Post-build script

