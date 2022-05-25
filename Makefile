.PHONY: login

.PHONY: create-new

.PHONY: dev-install-package

.PHONY: deploy

login:
	pollination-apps login -e staging

create-new:
	pollination-apps new

deploy:
	pollination-apps deploy . --tag $(TAG) --owner antonellodinunzio -n "direct-sun-hours-app" -e staging -m "$(COMMENT)"