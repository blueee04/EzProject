# EzProject - Discord Project Management Bot

A powerful Discord bot that facilitates group projects by assigning tasks, tracking progress, and enabling seamless communication within the team.

## Features

### ✅ Completed
- **MongoDB Integration** - Persistent data storage with MongoDB Atlas
- **Task Management** - Add, edit, delete, and list tasks
- **Project Organization** - Organize tasks by project IDs
- **Status Tracking** - Track task completion with visual indicators
- **Member Assignment** - Assign team members to specific tasks
- **Slash Commands** - Modern Discord slash command interface

### 🚧 In Progress
- **Enhanced Assignment System** - Database storage for assignments
- **Progress Analytics** - Project completion statistics
- **Notification System** - Task deadline reminders

### 📋 Planned
- **Bot Hosting** - Deploy to cloud platforms
- **Advanced Permissions** - Role-based access control
- **File Attachments** - Support for project files
- **Timeline View** - Project timeline visualization

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Discord Bot Token
- MongoDB Atlas account

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd EzProject
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory:
```env
BOT_TOKEN=your_discord_bot_token_here
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=discord
COLLECTION_NAME=tasks
COMMAND_PREFIX=!
```

### 4. Set Up Discord Bot
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section and create a bot
4. Copy the bot token and add it to your `.env` file
5. Enable the following bot permissions:
   - Send Messages
   - Use Slash Commands
   - Embed Links
   - Mention Everyone (for assignments)

### 5. Set Up MongoDB Atlas
1. Create a MongoDB Atlas account
2. Create a new cluster
3. Get your connection string
4. Add it to your `.env` file

### 6. Run the Bot

#### Option 1: Slash Commands (Recommended)
```bash
python slash_commands.py
```

#### Option 2: Prefix Commands
```bash
python commands.py
```

#### Option 3: Original Implementation
```bash
python main.py
```

## Available Commands

### Task Management
- `/addtask <project_id> <description> [status]` - Add a new task
- `/listtask <project_id>` - List all tasks in a project
- `/listall` - List all projects and their tasks
- `/edittask <project_id> <task_id> <new_description> [status]` - Edit a task
- `/deletetask <project_id> <task_id>` - Delete a specific task
- `/deleteproject <project_id>` - Delete an entire project

### Assignment Management
- `/assign <project_id> <task_id> <member>` - Assign a member to a task
- `/listassign <project_id>` - List assignments for a project

### Utility
- `/hello` - Say hello to the bot
- `/help` - Show all available commands
- `/status <project_id> <task_id> <status>` - Update task status

## Hosting Options

### Railway (Recommended)
1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically

### Heroku
1. Create a `Procfile`:
```
worker: python hosting_setup.py
```
2. Deploy using Heroku CLI or GitHub integration

### DigitalOcean App Platform
1. Connect your repository
2. Set environment variables
3. Deploy with automatic scaling

## Project Structure
```
EzProject/
├── main.py              # Original prefix command implementation
├── commands.py          # Updated prefix command implementation
├── slash_commands.py    # Modern slash command implementation
├── hosting_setup.py     # Production-ready hosting setup
├── config.py            # Configuration management
├── Datamodule/
│   ├── __init__.py
│   └── db.py           # Database operations
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/yourusername/EzProject/issues) page
2. Create a new issue with detailed information
3. Join our Discord server for community support

## Changelog

### v1.0.0
- Initial release with basic task management
- MongoDB integration
- Slash command support
- Member assignment system
