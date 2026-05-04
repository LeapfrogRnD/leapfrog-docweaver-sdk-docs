// ─── Sample documents used across all demo variants ──────────────────────────
import {
  FileText,
  Receipt,
  FileCheck,
  Building2,
  FileSignature,
  FileSpreadsheet,
} from 'lucide-react';
import type { DocumentSample } from './types';

export const sampleDocuments: DocumentSample[] = [
  {
    id: 'receipt',
    type: 'Receipt',
    name: 'Grocery Receipt',
    icon: Receipt,
    preview: '/sample-receipt.jpg',
    result: {
      structuredFields: [
        { key: 'Store Name', value: 'SUPER MARKET', confidence: 0.99 },
        { key: 'Receipt Number', value: '45678', confidence: 0.98 },
        { key: 'Date', value: '01/30/2026', confidence: 0.99 },
        { key: 'Time', value: '14:35', confidence: 0.98 },
        { key: 'Subtotal', value: '$21.95', confidence: 0.99 },
        { key: 'Tax', value: '$1.87', confidence: 0.99 },
        { key: 'Total', value: '$23.82', confidence: 0.99 },
        { key: 'Payment Method', value: 'Credit Card', confidence: 0.97 },
      ],
      processingTime: 1.8,
      rawResponse: {
        task_type: 'extraction',
        pipeline_id: 1,
        page_count: 1,
        processing_metadata: { llm_model: 'sample', llm_model_provider: 'sample' },
        results: [{ pg_no: 1, store_name: 'SUPER MARKET', receipt_number: '45678', date: '01/30/2026', time: '14:35', subtotal: '$21.95', tax: '$1.87', total: '$23.82', payment_method: 'Credit Card' }],
      },
    },
  },
  {
    id: 'invoice',
    type: 'Invoice',
    name: 'Business Invoice',
    icon: FileText,
    preview: '/sample-invoice.jpg',
    result: {
      structuredFields: [
        { key: 'Invoice Number', value: 'INV-2026-001', confidence: 0.98 },
        { key: 'Date', value: 'January 30, 2026', confidence: 0.99 },
        { key: 'Due Date', value: 'February 28, 2026', confidence: 0.97 },
        { key: 'Bill To', value: 'Acme Corporation', confidence: 0.96 },
        { key: 'Address', value: '123 Business St, San Francisco, CA 94103', confidence: 0.95 },
        { key: 'Subtotal', value: '$9,700.00', confidence: 0.99 },
        { key: 'Tax', value: '$824.50', confidence: 0.98 },
        { key: 'Total Amount', value: '$10,524.50', confidence: 0.99 },
        { key: 'Payment Terms', value: 'Net 30 days', confidence: 0.97 },
      ],
      processingTime: 2.3,
      rawResponse: {
        task_type: 'extraction',
        pipeline_id: 1,
        page_count: 1,
        processing_metadata: { llm_model: 'sample', llm_model_provider: 'sample' },
        results: [{ pg_no: 1, invoice_number: 'INV-2026-001', date: 'January 30, 2026', due_date: 'February 28, 2026', bill_to: 'Acme Corporation', address: '123 Business St, San Francisco, CA 94103', subtotal: '$9,700.00', tax: '$824.50', total_amount: '$10,524.50', payment_terms: 'Net 30 days' }],
      },
    },
  },
  {
    id: 'cheque',
    type: 'Cheque',
    name: 'Bank Check',
    icon: FileCheck,
    preview: '/sample-cheque.jpg',
    result: {
      structuredFields: [
        { key: 'Bank Name', value: 'FIRST NATIONAL BANK', confidence: 0.99 },
        { key: 'Check Number', value: '1234', confidence: 0.98 },
        { key: 'Date', value: 'January 30, 2026', confidence: 0.99 },
        { key: 'Pay To', value: 'Acme Corporation', confidence: 0.97 },
        { key: 'Amount', value: '$10,524.50', confidence: 0.99 },

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
        { key: 'Payment Terms', value: 'Net 30 days', confidence: 0.97 },
      ],
      processingTime: 2.3,
    },
  },
  {
    id: 'cheque',
    type: 'Cheque',
    name: 'Bank Check',
    icon: FileCheck,
    preview: '/sample-cheque.jpg',
    result: {
      rawText: `FIRST NATIONAL BANK
123 Bank Street, New York, NY 10001

Date: January 30, 2026                    Check #: 1234

Pay to the Order of: Acme Corporation     $10,524.50

Ten Thousand Five Hundred Twenty Four and 50/100 Dollars

Memo: Invoice INV-2026-001

Signature: ___________________

Routing Number: 021000021
Account Number: 1234567890`,
      structuredFields: [
        { key: 'Bank Name', value: 'FIRST NATIONAL BANK', confidence: 0.99 },
        { key: 'Check Number', value: '1234', confidence: 0.98 },
        { key: 'Date', value: 'January 30, 2026', confidence: 0.99 },
        { key: 'Pay To', value: 'Acme Corporation', confidence: 0.97 },
        { key: 'Amount', value: '$10,524.50', confidence: 0.99 },
        { key: 'Amount (Words)', value: 'Ten Thousand Five Hundred Twenty Four and 50/100 Dollars', confidence: 0.96 },
        { key: 'Memo', value: 'Invoice INV-2026-001', confidence: 0.95 },
        { key: 'Routing Number', value: '021000021', confidence: 0.98 },
        { key: 'Account Number', value: '1234567890', confidence: 0.98 },
      ],
      processingTime: 2.1,
    },
  },
  {
    id: 'bank-statement',
    type: 'Bank Statement',
    name: 'Monthly Statement',
    icon: Building2,
    preview: '/sample-bank-statement.jpg',
    result: {
      rawText: `FIRST NATIONAL BANK
Monthly Statement

Account Holder: John Doe
Account Number: 1234567890
Statement Period: January 1 - January 31, 2026

Beginning Balance (01/01/2026):    $25,430.75

Deposits and Credits:
01/05  Salary Deposit              $8,500.00
01/15  Transfer                    $2,000.00
01/28  Interest                       $12.45

Withdrawals and Debits:
01/08  Rent Payment               -$2,500.00
01/12  Grocery Store                -$234.56
01/20  Utilities                    -$156.78
01/25  Online Purchase              -$89.99

Ending Balance (01/31/2026):      $32,961.87

Questions? Call: 1-800-BANK-123`,
      structuredFields: [
        { key: 'Bank Name', value: 'FIRST NATIONAL BANK', confidence: 0.99 },
        { key: 'Account Holder', value: 'John Doe', confidence: 0.98 },
        { key: 'Account Number', value: '1234567890', confidence: 0.98 },
        { key: 'Statement Period', value: 'January 1 - January 31, 2026', confidence: 0.97 },
        { key: 'Beginning Balance', value: '$25,430.75', confidence: 0.99 },
        { key: 'Total Deposits', value: '$10,512.45', confidence: 0.98 },
        { key: 'Total Withdrawals', value: '$2,981.33', confidence: 0.98 },
        { key: 'Ending Balance', value: '$32,961.87', confidence: 0.99 },
      ],
      processingTime: 2.5,
    },
  },
  {
    id: 'w2',
    type: 'W-2 Form',
    name: 'Tax Form W-2',
    icon: FileSignature,
    preview: '/sample-w2.jpg',
    result: {
      rawText: `Form W-2 Wage and Tax Statement 2025

Employee Information:
Name: John A. Doe
SSN: ***-**-1234
Address: 456 Maple Street, Brooklyn, NY 11201

Employer Information:
Name: TechCorp Solutions Inc.
EIN: 12-3456789
Address: 789 Corporate Blvd, New York, NY 10001

Box 1 - Wages, tips, other compensation:     $85,000.00
Box 2 - Federal income tax withheld:         $12,750.00
Box 3 - Social security wages:               $85,000.00
Box 4 - Social security tax withheld:         $5,270.00
Box 5 - Medicare wages and tips:             $85,000.00
Box 6 - Medicare tax withheld:                $1,232.50
Box 16 - State wages, tips, etc.:            $85,000.00
Box 17 - State income tax:                    $4,675.00`,
      structuredFields: [
        { key: 'Form Type', value: 'W-2', confidence: 0.99 },
        { key: 'Tax Year', value: '2025', confidence: 0.99 },
        { key: 'Employee Name', value: 'John A. Doe', confidence: 0.98 },
        { key: 'Employee SSN', value: '***-**-1234', confidence: 0.97 },
        { key: 'Employer Name', value: 'TechCorp Solutions Inc.', confidence: 0.98 },
        { key: 'Employer EIN', value: '12-3456789', confidence: 0.98 },
        { key: 'Total Wages', value: '$85,000.00', confidence: 0.99 },
        { key: 'Federal Tax Withheld', value: '$12,750.00', confidence: 0.99 },
        { key: 'Social Security Tax', value: '$5,270.00', confidence: 0.99 },
        { key: 'Medicare Tax', value: '$1,232.50', confidence: 0.99 },
        { key: 'State Tax', value: '$4,675.00', confidence: 0.99 },
      ],
      processingTime: 2.8,
    },
  },
  {
    id: 'w9',
    type: 'W-9 Form',
    name: 'Tax Form W-9',
    icon: FileSpreadsheet,
    preview: '/sample-w9.jpg',
    result: {
      rawText: `Form W-9
Request for Taxpayer Identification Number and Certification

1. Name: John A. Doe

2. Business name/disregarded entity name: Doe Consulting LLC

3. Federal tax classification:
   [X] Individual/sole proprietor
   [ ] C Corporation
   [ ] S Corporation
   [ ] Partnership
   [ ] Trust/estate
   [ ] Limited liability company

4. Exemptions: N/A

5. Address: 456 Maple Street, Brooklyn, NY 11201

6. City, state, and ZIP code: Brooklyn, NY 11201

7. Account number(s): Optional

Part I: Taxpayer Identification Number (TIN)
Social Security Number: ***-**-1234
or
Employer Identification Number: __-_______

Part II: Certification
Under penalties of perjury, I certify that:
1. The number shown on this form is my correct taxpayer identification number
2. I am not subject to backup withholding

Signature: _________________ Date: 01/30/2026`,
      structuredFields: [
        { key: 'Form Type', value: 'W-9', confidence: 0.99 },
        { key: 'Name', value: 'John A. Doe', confidence: 0.98 },
        { key: 'Business Name', value: 'Doe Consulting LLC', confidence: 0.97 },
        { key: 'Tax Classification', value: 'Individual/sole proprietor', confidence: 0.98 },
        { key: 'Address', value: '456 Maple Street, Brooklyn, NY 11201', confidence: 0.97 },
        { key: 'SSN/TIN', value: '***-**-1234', confidence: 0.97 },
        { key: 'Date', value: '01/30/2026', confidence: 0.98 },
      ],
      processingTime: 2.2,
    },
  },
];
