# This makefile installing python libs required by components this makefile was ran for.
# Also those components adding to comp.conf file in order to be ran by run-script.
#
# When make without compoent list specified all component target will be made.

.DEFAULT_GOAL := all
SHELL = /bin/bash

################ Constants ################

COMPONENT_CONF_FILE := comp.conf
PIP_REQUIRE := requirements.txt

COMPONENTS := collector admingui graphgui logger
SERVICES :=
SERVERS := beanstalkd
TARGETS := all $(COMPONENTS) $(SERVICES) $(SERVERS)

################ Functions ################

echo_target_done = @echo Making $(1) done.

echo_target_started = @echo Making $(1).

define add_component
  @echo 'components+=( "$(1)" )' >> $(COMPONENT_CONF_FILE)
endef

define add_service
  @echo 'services+=( "$(1)" )' >> $(COMPONENT_CONF_FILE)
endef

define add_server
  @echo 'servers+=( "$(1)" )' >> $(COMPONENT_CONF_FILE)
endef

################  Targets  ################

.PHONY: $(TARGETS)

all: collector admingui graphgui logger
	$(call echo_target_done,$@)

collector:
	$(call echo_target_started,$@)
	$(call add_component,$@)
	$(call echo_target_done,$@)

admingui:
	$(call echo_target_started,$@)
	$(call echo_target_done,$@)

graphgui:
	$(call echo_target_started,$@)
	$(call echo_target_done,$@)

logger:
	$(call echo_target_started,$@)
	$(call add_component,$@)
	$(call echo_target_done,$@)

beanstalkd:
	$(call echo_target_started,$@)
	$(call add_server,$@)
	$(call echo_target_done,$@)

$(TARGETS): create_run_env

create_run_env:
	@echo Creating running environment.
	pip install -r $(PIP_REQUIRE)
	cp comp.conf.in comp.conf

