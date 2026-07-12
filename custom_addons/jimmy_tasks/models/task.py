# -*- coding: utf-8 -*-
from odoo import api, fields, models


class JimmyTask(models.Model):
    _name = "jimmy.task"
    _description = "Jimmy Task"
    _order = "priority desc, deadline asc, id desc"

    name = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description")
    deadline = fields.Date(string="Deadline")
    priority = fields.Selection(
        [("0", "Low"), ("1", "Normal"), ("2", "High")],
        string="Priority",
        default="1",
    )
    state = fields.Selection(
        [("todo", "To Do"), ("in_progress", "In Progress"), ("done", "Done")],
        string="Status",
        default="todo",
        required=True,
    )
    user_id = fields.Many2one(
        "res.users",
        string="Assigned to",
        default=lambda self: self.env.user,
    )
    is_overdue = fields.Boolean(
        string="Overdue", compute="_compute_is_overdue"
    )

    @api.depends("deadline", "state")
    def _compute_is_overdue(self):
        today = fields.Date.context_today(self)
        for task in self:
            task.is_overdue = bool(
                task.deadline
                and task.state != "done"
                and task.deadline < today
            )

    def action_start(self):
        self.write({"state": "in_progress"})

    def action_done(self):
        self.write({"state": "done"})

    def action_reset(self):
        self.write({"state": "todo"})
