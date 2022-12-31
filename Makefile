LINGUAS = en \
	  de \
	  zh_TW

default: help

help:
	@echo "Available targets:"
	@echo "  update           - update translations"

POTFILES = Bot_HereComesTheSun.py

update:
	xgettext --output=base.pot --output-dir=locales --language=Python --from-code=UTF-8 --add-comments  $(POTFILES)

	catalogs='$(LINGUAS)'; \
        for cat in $$catalogs; do \
	  msgmerge --update locales/$$cat/LC_MESSAGES/base.po locales/base.pot; \
	  msgfmt locales/$$cat/LC_MESSAGES/base.po --output locales/$$cat/LC_MESSAGES/base.mo; \
	done