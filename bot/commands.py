"""
This file has been refactored into separate modules for better organization.
The commands are now organized in the following files:

- bot/cogs/task_management.py - Task management commands (addtask, listtask, etc.)
- bot/cogs/assignment_management.py - Assignment commands (assign, unassign, etc.)
- bot/cogs/deadline_management.py - Deadline commands (deadline, overdue, etc.)
- bot/cogs/role_management.py - Role management commands (createrole, giverole, etc.)
- bot/cogs/utility_commands.py - Utility commands (hello, helpme, ping)

For backward compatibility, you can import from these individual modules.
"""

# Import all the new cogs for backward compatibility
from bot.cogs.task_management import TaskManagement
from bot.cogs.assignment_management import AssignmentManagement
from bot.cogs.deadline_management import DeadlineManagement
from bot.cogs.role_management import RoleManagement
from bot.cogs.utility_commands import UtilityCommands

# Legacy class that combines all commands (for backward compatibility)
class ProjectCommands(TaskManagement, AssignmentManagement, DeadlineManagement, RoleManagement, UtilityCommands):
    """
    Legacy class that combines all command categories.
    This is maintained for backward compatibility.
    New code should use the individual cog classes instead.
    """
    def __init__(self, bot):
        TaskManagement.__init__(self, bot)
        AssignmentManagement.__init__(self, bot)
        DeadlineManagement.__init__(self, bot)
        RoleManagement.__init__(self, bot)
        UtilityCommands.__init__(self, bot)

# Export the legacy class for backward compatibility
__all__ = ['ProjectCommands', 'TaskManagement', 'AssignmentManagement', 'DeadlineManagement', 'RoleManagement', 'UtilityCommands']