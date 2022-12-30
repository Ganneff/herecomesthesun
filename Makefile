LINGUAS = en \
	  de

default: help

help:
	@echo "Available targets:"
	@echo "  update           - update translations"

POTFILES = Bot_HereComesTheSun.py

update:
	pygettext3 --default-domain=base --output=base.pot --output-dir=locales $(POTFILES)

	catalogs='$(LINGUAS)'; \
        for cat in $$catalogs; do \
	  msgmerge --update locales/$$cat/LC_MESSAGES/base.po locales/base.pot; \
	  msgfmt locales/$$cat/LC_MESSAGES/base.po --output locales/$$cat/LC_MESSAGES/base.mo; \
	done