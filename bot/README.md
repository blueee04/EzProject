# EzProject Bot - Modular Structure

This directory contains the Discord bot for EzProject, organized in a modular structure for better maintainability.

## Directory Structure

```
bot/
├── main.py                    # Main bot entry point
├── commands.py               # Legacy compatibility file
├── slash_commands.py         # Slash command implementations
├── cogs/                     # Command modules (Cogs)
│   ├── __init__.py
│   ├── task_management.py    # Task-related commands
│   ├── assignment_management.py  # Assignment-related commands
│   ├── deadline_management.py    # Deadline-related commands
│   ├── role_management.py        # Role management commands
│   └── utility_commands.py       # Utility commands
└── utils/                    # Shared utilities
    ├── __init__.py
    └── permissions.py        # Permission checking utilities
```

## Command Categories

### Task Management (`cogs/task_management.py`)
- `!addtask` - Add a new task to a project
- `!listtask` - List all tasks in a project
- `!listall` - List all projects and their tasks
- `!edittask` - Edit an existing task
- `!deletetask` - Delete a task (Project Manager only)
- `!deleteproject` - Delete an entire project (Project Manager only)

### Assignment Management (`cogs/assignment_management.py`)
- `!assign` - Assign a task to a user
- `!unassign` - Remove assignment from a task
- `!listassign` - List all assignments for a project

### Deadline Management (`cogs/deadline_management.py`)
- `!deadline` - Set a deadline for a task
- `!overdue` - Show all overdue tasks
- `!duesoon` - Show tasks due within specified days

### Role Management (`cogs/role_management.py`)
- `!createrole` - Create a new role (Admin only)
- `!giverole` - Assign a role to a user (Admin only)
- `!removerole` - Remove a role from a user (Admin only)
- `!listroles` - List all roles in the server
- `!myroles` - Show roles for yourself or another user
- `!deleterole` - Delete a role (Admin only)

### Utility Commands (`cogs/utility_commands.py`)
- `!hello` - Greeting command
- `!helpme` - Show help information
- `!ping` - Check bot latency

## Shared Utilities

### Permissions (`utils/permissions.py`)
- `has_project_permission()` - Decorator for Project Manager role checks

## Usage

### Running the Bot
```bash
python bot/main.py
```

### Adding New Commands
1. Create a new file in the `cogs/` directory or add to an existing category
2. Follow the Cog pattern with proper setup function
3. Add the cog to the `load_cogs()` function in `main.py`

### Example Cog Structure
```python
import discord
from discord.ext import commands
from config.config import EMBED_COLORS

class MyCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mycommand")
    async def my_command(self, ctx):
        # Command implementation
        pass

async def setup(bot):
    await bot.add_cog(MyCommands(bot))
```

## Backward Compatibility

The original `commands.py` file has been replaced with a compatibility layer that imports all the new cogs. Existing code that imports `ProjectCommands` will continue to work.

## Benefits of This Structure

1. **Modularity**: Commands are organized by functionality
2. **Maintainability**: Easier to find and modify specific commands
3. **Scalability**: Easy to add new command categories
4. **Code Reuse**: Shared utilities reduce duplication
5. **Testing**: Individual modules can be tested separately 