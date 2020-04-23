# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import mock
from operator import attrgetter
from odoo import models


class TestExcludeLocationMixin(object):
    # Generate xmlids
    # This is needed if you want to load data tied to a test model via xid.
    _test_setup_gen_xid = False
    # If you extend a real model (ie: res.partner) you must enable this
    # to not delete the model on tear down.
    _test_teardown_no_delete = False
    # You can add custom fields to real models (eg: res.partner).
    # In this case you must delete them to leave registry and model clean.
    # This is mandatory for relational fields that link a fake model.
    _test_purge_fields = []

    @classmethod
    def _test_setup_model(cls, env):
        """Initialize it."""
        with mock.patch.object(env.cr, "commit"):
            cls._build_model(env.registry, env.cr)
            env.registry.setup_models(env.cr)
            ctx = dict(env.context, update_custom_fields=True)
            env.registry.init_models(env.cr, [cls._name], ctx)

    @classmethod
    def _test_teardown_model(cls, env):
        """Cleanup registry and real models."""

        for fname in cls._test_purge_fields:
            model = env[cls._name]
            if fname in model:
                model._pop_field(fname)

        if not getattr(cls, "_test_teardown_no_delete", False):
            del env.registry.models[cls._name]
            # here we must remove the model from list of children of inherited
            # models
            parents = cls._inherit
            parents = (
                [parents]
                if isinstance(parents, basestring)
                else (parents or [])
            )
            # keep a copy to be sure to not modify the original _inherit
            parents = list(parents)
            parents.extend(cls._inherits.keys())
            parents.append("base")
            funcs = [
                attrgetter(kind + "_children")
                for kind in ["_inherits", "_inherit"]
            ]
            for parent in parents:
                for func in funcs:
                    children = func(env.registry[parent])
                    if cls._name in children:
                        # at this stage our cls is referenced as children of
                        # parent -> must un reference it
                        children.remove(cls._name)


class ExcludeLocationModelFake(models.Model, TestExcludeLocationMixin):

    _name = "exclude.location.fake"
    _inherit = "stock.exclude.location.mixin"
    _description = "Exclude Location Fake"
