SUBDIRS := docs

all: $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@ html

.PHONY: all $(SUBDIRS)
