LINGUAS = en \
	  de \
	  zh_TW

default: help

help:
	@echo "Available targets:"
	@echo "  update           - update translations"

POTFILES = Bot_HereComesTheSun.py toot.tmpl diff.tmpl

update:
	pybabel extract -F babel.cfg --output=locales/base.pot --sort-by-file --add-comments=transcomment --copyright-holder="Joerg Jaspert" --msgid-bugs-address="https://codeberg.org/Fulda.Social/herecomesthesun/issues" --project "HereComesTheSunBot" $(POTFILES)

	catalogs='$(LINGUAS)'; \
        for cat in $$catalogs; do \
	  msgmerge --update locales/$$cat/LC_MESSAGES/base.po locales/base.pot; \
	  msgfmt locales/$$cat/LC_MESSAGES/base.po --output locales/$$cat/LC_MESSAGES/base.mo; \
	done
