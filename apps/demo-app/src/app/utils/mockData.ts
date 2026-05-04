import { Task, OCRResult } from '../types';

// Mock OCR results for demo purposes
export const mockOCRResults: Record<string, OCRResult> = {
  invoice: {
    rawText: `INVOICE
Invoice Number: INV-2026-001
Date: January 30, 2026
Due Date: February 28, 2026

Bill To:
Acme Corporation
123 Business St
San Francisco, CA 94103

Items:
1. Professional Services    $5,000.00
2. Consulting Hours         $3,500.00
3. Software License         $1,200.00

Subtotal:                   $9,700.00
Tax (8.5%):                   $824.50
Total:                     $10,524.50

Payment Terms: Net 30 days
Thank you for your business!`,
    structuredFields: [
      { key: 'Invoice Number', value: 'INV-2026-001', confidence: 0.98 },
      { key: 'Date', value: 'January 30, 2026', confidence: 0.99 },
      { key: 'Due Date', value: 'February 28, 2026', confidence: 0.97 },
      { key: 'Bill To', value: 'Acme Corporation', confidence: 0.96 },
      { key: 'Address', value: '123 Business St, San Francisco, CA 94103', confidence: 0.95 },
      { key: 'Subtotal', value: '$9,700.00', confidence: 0.99 },
      { key: 'Tax', value: '$824.50', confidence: 0.98 },
      { key: 'Total Amount', value: '$10,524.50', confidence: 0.99 },
      { key: 'Payment Terms', value: 'Net 30 days', confidence: 0.97 }
    ],
    processingTime: 2.3
  },
  receipt: {
    rawText: `SUPER MARKET
123 Main Street
New York, NY 10001
Tel: (555) 123-4567

Receipt #: 45678
Date: 01/30/2026 14:35

Items:
Organic Apples        $4.99
Whole Wheat Bread     $3.49
Almond Milk          $5.99
Fresh Spinach        $2.99
Greek Yogurt         $4.49

Subtotal:           $21.95
Tax:                 $1.87
Total:              $23.82

Payment Method: Credit Card
Card: **** **** **** 1234

Thank you for shopping with us!`,
    structuredFields: [
      { key: 'Store Name', value: 'SUPER MARKET', confidence: 0.99 },
      { key: 'Receipt Number', value: '45678', confidence: 0.98 },
      { key: 'Date', value: '01/30/2026', confidence: 0.99 },
      { key: 'Time', value: '14:35', confidence: 0.98 },
      { key: 'Subtotal', value: '$21.95', confidence: 0.99 },
      { key: 'Tax', value: '$1.87', confidence: 0.99 },
      { key: 'Total', value: '$23.82', confidence: 0.99 },
      { key: 'Payment Method', value: 'Credit Card', confidence: 0.97 }
    ],
    processingTime: 1.8
  },
  contract: {
    rawText: `SERVICE AGREEMENT

This Service Agreement ("Agreement") is entered into on January 30, 2026
between TechCorp Solutions ("Provider") and Global Industries Inc. ("Client").

1. SERVICES
Provider agrees to deliver cloud infrastructure management services including
24/7 monitoring, maintenance, and technical support.

2. TERM
This Agreement shall commence on February 1, 2026 and continue for a period
of twelve (12) months, unless terminated earlier in accordance with Section 5.

3. COMPENSATION
Client shall pay Provider a monthly fee of $15,000, payable on the first
business day of each month.

4. CONFIDENTIALITY
Both parties agree to maintain confidentiality of proprietary information
shared during the term of this Agreement.

5. TERMINATION
Either party may terminate this Agreement with 30 days written notice.

Authorized Signatures:
Provider: _________________ Date: __________
Client: ___________________ Date: __________`,
    structuredFields: [
      { key: 'Document Type', value: 'Service Agreement', confidence: 0.99 },
      { key: 'Agreement Date', value: 'January 30, 2026', confidence: 0.98 },
      { key: 'Provider', value: 'TechCorp Solutions', confidence: 0.97 },
      { key: 'Client', value: 'Global Industries Inc.', confidence: 0.97 },
      { key: 'Commencement Date', value: 'February 1, 2026', confidence: 0.96 },
      { key: 'Term Length', value: '12 months', confidence: 0.95 },
      { key: 'Monthly Fee', value: '$15,000', confidence: 0.98 },
      { key: 'Termination Notice', value: '30 days', confidence: 0.96 }
    ],
    processingTime: 3.1
  }
};

// Demo tasks for initial display
export const demoTasks: Task[] = [
  {
    id: 'demo-1',
    name: 'Q4 2025 Invoice Processing',
    documents: [
      {
        id: 'doc-1',
        name: 'invoice_2025_Q4.pdf',
        size: 245678,
        type: 'application/pdf',
        uploadedAt: new Date('2026-01-28T10:30:00')
      }
    ],
    pipeline: {
      type: 'invoice',
      extractionMode: 'both'
    },
    status: 'completed',
    createdAt: new Date('2026-01-28T10:30:00'),
    completedAt: new Date('2026-01-28T10:32:30'),
    result: mockOCRResults.invoice
  },
  {
    id: 'demo-2',
    name: 'Expense Receipt Scan',
    documents: [
      {
        id: 'doc-2',
        name: 'receipt_jan_2026.jpg',
        size: 156234,
        type: 'image/jpeg',
        uploadedAt: new Date('2026-01-29T15:45:00')
      }
    ],
    pipeline: {
      type: 'receipt',
      extractionMode: 'both'
    },
    status: 'completed',
    createdAt: new Date('2026-01-29T15:45:00'),
    completedAt: new Date('2026-01-29T15:47:00'),
    result: mockOCRResults.receipt
  },
  {
    id: 'demo-3',
    name: 'Service Contract Review',
    documents: [
      {
        id: 'doc-3',
        name: 'service_agreement_2026.pdf',
        size: 389012,
        type: 'application/pdf',
        uploadedAt: new Date('2026-01-30T09:00:00')
      }
    ],
    pipeline: {
      type: 'contract',
      extractionMode: 'both'
    },
    status: 'processing',
    createdAt: new Date('2026-01-30T09:00:00')
  }
];

// Simulate OCR processing
export const simulateOCRProcessing = async (
  documentName: string,
  pipelineType: string
): Promise<OCRResult> => {
  // Simulate processing delay (2-5 seconds)
  const delay = 2000 + Math.random() * 3000;
  await new Promise(resolve => setTimeout(resolve, delay));

  // Random chance of failure for demo purposes (10%)
  if (Math.random() < 0.1) {
    throw new Error('OCR processing failed: Unable to extract text from document');
  }

  // Return appropriate mock result based on pipeline type
  if (mockOCRResults[pipelineType]) {
    return mockOCRResults[pipelineType];
  }

  // Default generic result
  return {
    rawText: `Document: ${documentName}\n\nExtracted text content would appear here.\n\nThis is a simulated OCR result for demonstration purposes.\nThe actual OCR engine would extract real text from the uploaded document.`,
    structuredFields: [
      { key: 'Document Name', value: documentName, confidence: 0.99 },
      { key: 'Processing Date', value: new Date().toLocaleDateString(), confidence: 0.99 },
      { key: 'Status', value: 'Processed', confidence: 0.98 }
    ],
    processingTime: delay / 1000
  };
};