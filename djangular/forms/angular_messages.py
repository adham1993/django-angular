# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.html import format_html
from django.utils.encoding import python_2_unicode_compatible, force_text
from django.utils.safestring import mark_safe, SafeText

from djangular.forms.angular_base import TupleErrorList, SafeTuple, NgFormBaseMixin


@python_2_unicode_compatible
class NgMessagesTupleErrorList(TupleErrorList):
	
    msgs_format = '<div class="{1}" ng-messages="{0}.$error" ng-show="{0}.$dirty && {0}.$invalid" ng-cloak>{2}</div>'
    msg_format = '<div ng-message="{1}" class="{2}">{3}</div>'
    """ span's necessary due to this bug https://github.com/angular/angular.js/issues/8089"""
    msg_format_bind = '<div ng-message="{1}" class="{2}"><span ng-bind="{0}.{3}.{1}"></span></div>'

    def __str__(self):
        return self.as_divs()

    def as_divs(self):
        if not self:
            return SafeText()
        first = self[0]
        if isinstance(first, tuple):
            error_list = []
            for e in self:
                if e[3] == '$valid':
                    continue
                msg_format = e[5] == '$message' and self.msg_format_bind or self.msg_format
                msg_type = e[3].split('.')
                err_tuple = (e[0], msg_type[0] if len(msg_type) == 1 else msg_type.pop(), e[4], force_text(e[5]))
                error_list.append(format_html(msg_format, *err_tuple))

        return (error_list and \
             format_html(self.msgs_format, first[0], first[1], mark_safe(''.join(error_list)))
          or '')


class NgMessagesMixin(NgFormBaseMixin):
	
    def __init__(self, data=None, *args, **kwargs):
        kwargs['error_class'] = NgMessagesTupleErrorList
        super(NgMessagesMixin, self).__init__(data, *args, **kwargs)

    def get_field_errors(self, field):
        errors = super(NgMessagesMixin, self).get_field_errors(field)
        if field.is_hidden:
            return errors
        #remove error added by NgModelFormMixin
        for item in errors[:]:
            if item[2] == '$pristine' and item[5] == '$message':
                errors.remove(item)
        identifier = format_html('{0}.{1}', self.form_name, field.name)
        errors.append(SafeTuple((identifier, self.field_error_css_classes, '$dirty', 'rejected', 'invalid', '$message')))
        return errors

    def get_widget_attrs(self, bound_field):
        attrs = super(NgMessagesMixin, self).get_widget_attrs(bound_field)
        attrs['validate-rejected'] = ""
        return attrs