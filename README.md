# LEAP X - OCR System

A comprehensive OCR (Optical Character Recognition) document processing system built with React, TypeScript, Tailwind CSS, and Shadcn UI components. This frontend application demonstrates a complete workflow for document upload, OCR processing, and result management.

## 🎨 Brand Identity

**Primary Color Palette:**
- **Brand Green**: `#038E43` - Main brand color for CTAs, icons, and interactive elements
- **Black**: `#111111` - Text and headers
- **Gray**: `#333333` - Secondary text and borders  
- **Ivory**: `#D9D9D9` - Backgrounds and dividers
- **White**: `#FFFFFF` - Cards and backgrounds

See [COLOR_PALETTE.md](./COLOR_PALETTE.md) for complete color documentation.

## 🚀 Features

### User Authentication
- Secure login interface with form validation
- Mock authentication system (any email + password with 6+ characters)
- Session management with logout functionality

### Task Management
- **Task List Dashboard**: View all OCR processing tasks at a glance
- **Task Statistics**: Real-time counts of total, completed, processing, and failed tasks
- **Task Creation**: Multi-step wizard for creating new OCR tasks
- **Task Details**: Comprehensive view of task status, documents, and results
- **Pipeline Management**: Create, edit, and manage reusable OCR pipeline templates (NEW!)

### Document Upload
- **Drag-and-Drop Interface**: Easy file uploads with visual feedback
- **File Validation**: 
  - Supported formats: PDF, JPG, PNG
  - Maximum file size: 10MB
  - Real-time error handling
- **Document Preview**: View uploaded files with size and type information
- **Multi-file Support**: Upload multiple documents per task

### OCR Pipeline Configuration
- **Pipeline Management Page**: Centralized location to create and manage reusable pipeline templates
- **Pre-configured Pipelines**:
  - **Default**: General purpose text extraction
  - **Invoice**: Extract invoice numbers, amounts, dates, and line items
  - **Receipt**: Extract purchase details, totals, and payment information
  - **Contract**: Extract terms, parties, and key clauses
  - **Custom**: Define your own extraction fields
- **Extraction Modes**:
  - Text Only: Extract raw text content
  - Classification: Structured field extraction
  - Both: Comprehensive extraction with raw text and structured data
- **Custom Fields**: Add dynamic fields for specific extraction needs
- **Pipeline Actions**: Create, edit, duplicate, delete, and set default pipelines

### Processing & Results
- **Real-time Status Updates**: Track processing through queued, processing, completed, and failed states
- **Progress Indicators**: Visual feedback during OCR processing
- **Structured Results**: 
  - Extracted key-value pairs with confidence scores
  - Organized display of document fields
  - Raw text extraction view
- **Processing Metadata**: Timestamps, processing time, and task information

### Export Functionality
- **JSON Export**: Download complete task results with metadata
- **Structured Format**: Includes task details, documents, and OCR results
- **One-Click Download**: Easy export for integration with other systems

## 📋 User Flow

```
1. Login Page
   ↓
2. Task List Dashboard
   ↓
3. Create New Task
   ├─ Step 1: Enter task name
   ├─ Step 2: Upload documents
   └─ Step 3: Configure pipeline
   ↓
4. Processing (Automatic)
   ├─ Queued → Processing → Completed/Failed
   └─ Real-time status updates
   ↓
5. View Results
   ├─ Structured fields with confidence scores
   ├─ Raw extracted text
   └─ Export to JSON
```

## 🎨 Design Features

- **Responsive Layout**: Fully responsive design that works on desktop, tablet, and mobile
- **Modern UI**: Clean, professional interface with Tailwind CSS
- **Accessibility**: WCAG AA compliant with proper contrast and keyboard navigation
- **Visual Feedback**: Loading states, hover effects, and smooth transitions
- **Status Indicators**: Color-coded badges and icons for different states
- **Empty States**: Helpful guidance when no tasks exist

## 🛠️ Technology Stack

- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe development
- **Tailwind CSS v4**: Utility-first styling
- **Lucide React**: Beautiful, consistent icons
- **date-fns**: Date formatting and manipulation
- **Shadcn UI**: Reusable UI components

## 📦 Project Structure

```
src/
├── app/
│   ├── components/
│   │   ├── Login.tsx              # Authentication interface
│   │   ├── TaskList.tsx           # Task dashboard and list
│   │   ├── CreateTask.tsx         # Multi-step task creation wizard
│   │   ├── DocumentUpload.tsx     # File upload with drag-and-drop
│   │   ├── PipelineConfig.tsx     # OCR pipeline configuration
│   │   ├── PipelineManagement.tsx # Pipeline template management (NEW!)
│   │   └── TaskDetail.tsx         # Task details and results viewer
│   ├── utils/
│   │   └── mockData.ts            # Mock OCR data and simulation
│   ├── types.ts                   # TypeScript type definitions
│   └── App.tsx                    # Main application component
└── styles/
    ├── theme.css                  # Design tokens and variables
    └── fonts.css                  # Font imports
```

## 📚 Documentation

- **[README.md](./README.md)** - This file, main project overview
- **[COLOR_PALETTE.md](./COLOR_PALETTE.md)** - Complete color system documentation
- **[PIPELINE_MANAGEMENT.md](./PIPELINE_MANAGEMENT.md)** - Pipeline Management feature guide (NEW!)
- **[QUICK_START.md](./QUICK_START.md)** - Quick start guide
- **[IMPLEMENTATION_NOTES.md](./IMPLEMENTATION_NOTES.md)** - Technical implementation details
- **[SHADCN_COMPONENTS.md](./SHADCN_COMPONENTS.md)** - UI component documentation
- **[PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)** - High-level project summary

## 🎯 Key Components

### Login Component
- Email and password authentication
- Form validation and error handling
- Demo credentials display
- Responsive design with gradient background

### Task List Component
- Dashboard with statistics cards
- Sortable task table
- Status badges and icons
- Quick actions (view, create)

### Create Task Component
- Three-step wizard interface
- Progress indicator
- Form validation at each step
- Back/Next navigation

### Document Upload Component
- Drag-and-drop zone
- File type and size validation
- Upload progress
- Document list with remove functionality

### Pipeline Config Component
- Visual pipeline selection
- Extraction mode options
- Custom field management
- Configuration summary

### Task Detail Component
- Complete task information
- Processing status indicators
- Structured field display with confidence scores
- Raw text viewer
- JSON export functionality

### Pipeline Management Component (NEW!)
- Centralized pipeline template management
- Create, edit, duplicate, and delete pipelines
- Set default pipeline for quick task creation
- Statistics dashboard (total, default, custom pipelines)
- Pre-loaded demo pipelines (Invoice, Receipt, Contract)
- Visual pipeline type and extraction mode selection
- Custom field configuration
- See [PIPELINE_MANAGEMENT.md](./PIPELINE_MANAGEMENT.md) for detailed documentation

## 🔧 Getting Started

### Demo Credentials
Use any email address and a password with at least 6 characters to log in.

Example:
- Email: `demo@leapx.com`
- Password: `password123`

### Sample Tasks
The application comes pre-loaded with three demo tasks:
1. **Q4 2025 Invoice Processing** (Completed)
2. **Expense Receipt Scan** (Completed)
3. **Service Contract Review** (Processing)

### Creating a New Task

1. Click "Create New Task" button
2. Enter a descriptive task name
3. Upload your documents (PDF, JPG, or PNG)
4. Select a pipeline type or configure custom extraction
5. Choose extraction mode
6. Click "Create & Process Task"

The task will automatically begin processing and you'll be redirected to the task list where you can monitor progress.

### Viewing Results

1. Navigate to the task list
2. Click "View" on any completed task
3. Review extracted fields and raw text
4. Click "Export JSON" to download results

### Managing Pipelines (NEW!)

1. From the Task List, click "Pipeline Configuration" in the header
2. View all saved pipeline templates with statistics
3. **Create New Pipeline**:
   - Click "New Pipeline"
   - Enter name and description
   - Select pipeline type and extraction mode
   - Add custom fields
   - Click "Create Pipeline"
4. **Edit Pipeline**: Click the edit (pencil) icon on any pipeline card
5. **Duplicate Pipeline**: Click the duplicate (copy) icon to create a variant
6. **Set Default**: Click the star icon to set a pipeline as default
7. **Delete Pipeline**: Click the trash icon (cannot delete default pipeline)

See [PIPELINE_MANAGEMENT.md](./PIPELINE_MANAGEMENT.md) for comprehensive feature documentation.

## 📊 Mock Data

The application includes realistic mock OCR results for demonstration:

- **Invoice**: Extract invoice numbers, dates, billing information, line items, and totals
- **Receipt**: Extract store information, items, prices, and payment details
- **Contract**: Extract agreement terms, parties, dates, and key clauses

Mock processing includes:
- Simulated processing delay (2-5 seconds)
- Random failure rate (10%) for testing error handling
- Confidence scores for extracted fields
- Processing time metadata

## 🎨 UI Guidelines

- **12-column responsive grid layout**
- **Spacing scale**: 4px, 8px, 16px, 24px, 32px
- **Typography hierarchy**: Clear distinction between headings, body, and captions
- **Color system**: 
  - Primary: Indigo (actions, focus)
  - Success: Green (completed)
  - Warning: Yellow (queued)
  - Error: Red (failed)
  - Info: Blue (processing)
- **Interactive states**: Hover, focus, active, and disabled states
- **Animations**: Smooth transitions under 300ms
- **Feedback**: Toast notifications and inline validation

## 🔐 Security Notes

This is a **frontend-only demonstration application**. In a production environment:

- Implement proper authentication with secure backend APIs
- Store credentials securely (never in frontend code)
- Use HTTPS for all communications
- Implement proper session management
- Add rate limiting and abuse prevention
- Validate and sanitize all user inputs on the backend
- Store sensitive data encrypted at rest

## 🚫 Out of Scope

This implementation does not include:
- Real backend/server/API integration
- Persistent data storage (database)
- Real OCR processing engine
- User registration/password reset
- Multi-user support
- Real-time notifications
- File storage service
- External service integrations

## 📝 Future Enhancements

Potential features for future iterations:
- Real OCR integration (Tesseract, Google Vision, AWS Textract)
- Batch processing for multiple documents
- Advanced search and filtering
- Task scheduling and automation
- Collaboration features
- Version history for processed documents
- Analytics and reporting dashboard
- API integration for external systems
- Webhook notifications
- Document comparison tools

## 🤝 Usage Tips

1. **Task Naming**: Use descriptive names like "Q1 2026 Invoices" or "January Expense Reports"
2. **Pipeline Selection**: Choose the pipeline that best matches your document type
3. **Custom Fields**: Use custom pipelines when you need to extract specific, non-standard fields
4. **Extraction Mode**: Select "Both" for comprehensive results
5. **File Quality**: Higher resolution images produce better OCR results
6. **Export**: Download JSON results for integration with other systems

## 📄 License

This is a demonstration project for the LEAP X OCR System.

## 🙋 Support

For questions or issues with this demo application, please refer to the PRD document or contact the development team.

---

**Built with ❤️ for enterprise document processing**