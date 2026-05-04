// ─── Workflow definitions + sample documents ─────────────────────────────────
import {
  Layers,
  Stethoscope,
  BookOpen,
  ShoppingCart,
  Zap,
  FileText,
  ClipboardList,
  Activity,
  FilePlus2,
  BookMarked,
  BarChart3,
  Scale,
} from "lucide-react";
import type { Workflow, ClassificationJsonSchema } from "./types";

export const workflows: Workflow[] = [
  // ── 1. Invoice Data Extraction ─────────────────────────────────────────────
  {
    id: "invoice",
    title: "Invoice Data Extraction",
    subtitle: "3 sample documents",
    icon: Layers,
    workflowType: "extraction",
    pipelineId: 1,
    additionalInstruction:
      "Extract all monetary values with their currency symbols. If a field is missing, return null.",
    jsonSchema: [
      {
        name: "invoice_number",
        type: "string",
        description: "The unique invoice identifier",
        required: true,
      },
      {
        name: "invoice_date",
        type: "string",
        description: "Date the invoice was issued",
        required: true,
      },
      { name: "due_date", type: "string", description: "Payment due date" },
      {
        name: "vendor_name",
        type: "string",
        description: "Name of the vendor or seller",
        required: true,
      },
      {
        name: "vendor_address",
        type: "string",
        description: "Address of the vendor",
      },
      {
        name: "customer_name",
        type: "string",
        description: "Name of the customer or buyer",
        required: true,
      },
      {
        name: "customer_address",
        type: "string",
        description: "Address of the customer",
      },
      {
        name: "line_items",
        type: "array",
        description:
          "List of items with description, quantity, unit price, and total",
      },
      {
        name: "subtotal",
        type: "float",
        description: "Subtotal amount before tax and discounts",
      },
      { name: "tax_amount", type: "float", description: "Total tax amount" },
      {
        name: "discount",
        type: "float",
        description: "Discount applied, if any",
      },
      {
        name: "total_amount",
        type: "float",
        description: "Final total amount due",
        required: true,
      },
      {
        name: "payment_method",
        type: "string",
        description: "Payment method used or accepted",
      },
      {
        name: "payment_terms",
        type: "string",
        description: "Payment terms (e.g., Net 30)",
      },
    ],
    documents: [
      {
        id: "retail-invoice",
        type: "Retail Invoice",
        name: "Retail Invoice",
        icon: ShoppingCart,
        preview: "",
        result: {
          rawText: `CITY RETAIL STORE
456 Commerce Ave, New York, NY 10002
Tel: (212) 555-0198

INVOICE #: RI-20260130-007
Date: January 30, 2026

Bill To:
Jane Smith
789 Oak Street, Brooklyn, NY 11201

Items Purchased:
  Wireless Headphones (SKU: WH-300)     $129.99
  USB-C Charging Cable × 2 (SKU: CC-12)   $24.98
  Laptop Stand (SKU: LS-45)              $49.99
  Screen Cleaning Kit (SKU: SK-08)        $14.99

Subtotal:                               $219.95
Sales Tax (8.875%):                      $19.52
Shipping & Handling:                      $9.99
TOTAL:                                  $249.46

Payment: Visa **** 4821 — Approved
Thank you for shopping with City Retail!`,
          structuredFields: [
            { key: "Store Name", value: "CITY RETAIL STORE", confidence: 0.99 },
            {
              key: "Invoice Number",
              value: "RI-20260130-007",
              confidence: 0.98,
            },
            { key: "Date", value: "January 30, 2026", confidence: 0.99 },
            { key: "Customer", value: "Jane Smith", confidence: 0.97 },
            { key: "Subtotal", value: "$219.95", confidence: 0.99 },
            { key: "Sales Tax", value: "$19.52", confidence: 0.98 },
            { key: "Shipping", value: "$9.99", confidence: 0.98 },
            { key: "Total", value: "$249.46", confidence: 0.99 },
            {
              key: "Payment Method",
              value: "Visa **** 4821",
              confidence: 0.97,
            },
          ],
          processingTime: 1.6,
        },
      },
      {
        id: "utility-bill",
        type: "Utility Bill",
        name: "Utility Bill",
        icon: Zap,
        preview: "",
        result: {
          rawText: `METRO ENERGY SERVICES
PO Box 1200, Albany, NY 12201
Customer Service: 1-800-555-0142

ELECTRICITY BILL

Account Number:   4872-1093-X
Customer:         Robert Chen
Service Address:  22 Maple Drive, Queens, NY 11374
Billing Period:   Jan 1 – Jan 31, 2026
Due Date:         February 15, 2026

CURRENT CHARGES
Previous Balance:                         $0.00
Energy Usage (842 kWh × $0.1423):       $119.82
Delivery Charge:                          $18.50
Renewable Energy Surcharge:               $4.20
State/Local Taxes:                        $11.30
TOTAL AMOUNT DUE:                        $153.82

Energy Usage This Month: 842 kWh
Avg Daily Usage: 27.2 kWh
vs. Last Month:  -8%
vs. Same Month Last Year: +3%`,
          structuredFields: [
            {
              key: "Utility Provider",
              value: "METRO ENERGY SERVICES",
              confidence: 0.99,
            },
            { key: "Account Number", value: "4872-1093-X", confidence: 0.98 },
            { key: "Customer Name", value: "Robert Chen", confidence: 0.98 },
            {
              key: "Service Address",
              value: "22 Maple Drive, Queens, NY 11374",
              confidence: 0.96,
            },
            {
              key: "Billing Period",
              value: "Jan 1 – Jan 31, 2026",
              confidence: 0.97,
            },
            { key: "Due Date", value: "February 15, 2026", confidence: 0.98 },
            { key: "Energy Usage", value: "842 kWh", confidence: 0.99 },
            { key: "Total Amount Due", value: "$153.82", confidence: 0.99 },
          ],
          processingTime: 1.9,
        },
      },
    ],
  },

  // ── 2. Medical Data Classification ─────────────────────────────────────────
  {
    id: "medical",
    title: "Medical Data Classification",
    subtitle: "3 sample documents",
    icon: Stethoscope,
    workflowType: "classification",
    pipelineId: 1,
    additionalInstruction:
      "Classify the document type first, then extract clinical fields. Use ICD-10 codes for diagnoses where available.",
    jsonSchema: [
      {
        category: "document_type",
        fields: [
          {
            name: "Patient Visit Report",
            description:
              "A clinical note documenting a patient encounter, vitals, and treatment plan.",
          },
          {
            name: "Lab Test Result",
            description:
              "A report of laboratory tests with measured values and reference ranges.",
          },
          {
            name: "Prescription",
            description:
              "A physician-issued medication order with dosage and refill instructions.",
          },
          {
            name: "Discharge Summary",
            description:
              "A summary of a patient's hospital stay, diagnosis, and follow-up plan.",
          },
          {
            name: "Radiology Report",
            description:
              "Findings from imaging studies such as X-ray, MRI, or CT scan.",
          },
        ],
      },
      {
        category: "severity",
        fields: [
          {
            name: "Critical",
            description:
              "Life-threatening condition requiring immediate emergency intervention.",
          },
          {
            name: "Severe",
            description:
              "Serious condition that significantly impacts patient health or function.",
          },
          {
            name: "Moderate",
            description:
              "Notable condition requiring active medical management but not immediately life-threatening.",
          },
          {
            name: "Mild",
            description:
              "Minor condition with limited impact on daily activities or overall health.",
          },
          {
            name: "Routine",
            description:
              "Standard preventive care or administrative document with no urgent clinical concerns.",
          },
        ],
      },
      {
        category: "department",
        fields: [
          {
            name: "Internal Medicine",
            description:
              "Documents related to general internal medicine consultations and management.",
          },
          {
            name: "Cardiology",
            description:
              "Documents relating to heart conditions, ECGs, or cardiac procedures.",
          },
          {
            name: "Pathology",
            description:
              "Lab-generated documents from pathology or clinical laboratory departments.",
          },
          {
            name: "Pharmacy",
            description: "Prescription and medication-management documents.",
          },
          {
            name: "Emergency",
            description:
              "Documents generated during emergency or urgent care encounters.",
          },
        ],
      },
      {
        category: "priority",
        fields: [
          {
            name: "Urgent",
            description:
              "Document requires immediate review or clinical action.",
          },
          {
            name: "High",
            description:
              "Document should be reviewed within the same business day.",
          },
          {
            name: "Normal",
            description:
              "Document can be handled within the standard workflow timeline.",
          },
          {
            name: "Low",
            description:
              "Document can be reviewed at a later time with no immediate urgency.",
          },
        ],
      },
    ] satisfies ClassificationJsonSchema,
    documents: [
      {
        id: "medical-report",
        type: "Medical Report",
        name: "Medical Report",
        icon: ClipboardList,
        preview: "",
        result: {
          rawText: `PATIENT VISIT REPORT
Greenfield Medical Center — Internal Medicine

Patient:        Sarah Johnson
DOB:            04/15/1985 (Age 40)
MRN:            GMC-00294817
Visit Date:     January 30, 2026
Provider:       Dr. Michael Torres, MD
Facility:       Greenfield Medical Center

CHIEF COMPLAINT
Patient presents with persistent fatigue, mild shortness of breath on exertion, and occasional palpitations over the past 3 weeks.

VITAL SIGNS
Blood Pressure:   128/82 mmHg
Heart Rate:       88 bpm (regular)
Temperature:      98.6°F
SpO2:             97%
Weight:           152 lbs

ASSESSMENT & PLAN
Primary Diagnosis: Iron-Deficiency Anemia (D50.9)
Secondary:        Mild Hypertension (I10)

Plan:
1. Ferrous sulfate 325mg PO twice daily × 8 weeks
2. Lisinopril 5mg PO once daily
3. CBC repeat in 6 weeks
4. Dietary counseling for iron-rich foods
5. Return in 6 weeks or sooner if symptoms worsen

Electronically signed: Dr. Michael Torres, MD
License: NY-MD-489201`,
          structuredFields: [
            { key: "Patient Name", value: "Sarah Johnson", confidence: 0.99 },
            { key: "Date of Birth", value: "04/15/1985", confidence: 0.98 },
            { key: "MRN", value: "GMC-00294817", confidence: 0.98 },
            { key: "Visit Date", value: "January 30, 2026", confidence: 0.99 },
            {
              key: "Provider",
              value: "Dr. Michael Torres, MD",
              confidence: 0.98,
            },
            { key: "Blood Pressure", value: "128/82 mmHg", confidence: 0.99 },
            { key: "Heart Rate", value: "88 bpm", confidence: 0.99 },
            {
              key: "Primary Diagnosis",
              value: "Iron-Deficiency Anemia (D50.9)",
              confidence: 0.97,
            },
            {
              key: "Secondary Diagnosis",
              value: "Mild Hypertension (I10)",
              confidence: 0.96,
            },
          ],
          processingTime: 2.4,
        },
      },

      {
        id: "prescription",
        type: "Prescription",
        name: "Prescription",
        icon: FilePlus2,
        preview: "",
        result: {
          rawText: `Rx PRESCRIPTION

Prescriber:   Dr. Michael Torres, MD
              Greenfield Medical Center
              123 Health Blvd, New York, NY 10003
              DEA: BT4829301 | NPI: 1234567890
              Phone: (212) 555-0103

Date:         January 30, 2026

Patient:      Sarah Johnson
DOB:          04/15/1985
Address:      45 Elm St, Manhattan, NY 10001

─────────────────────────────────────────────────
Rx 1:  Ferrous Sulfate 325mg (65mg elemental iron)
       Sig: Take 1 tablet by mouth TWICE daily with food
       Disp: #60 (sixty) tablets
       Refills: 2
       Generic substitution permitted

Rx 2:  Lisinopril 5mg tablets
       Sig: Take 1 tablet by mouth ONCE daily
       Disp: #30 (thirty) tablets
       Refills: 3
       Generic substitution permitted
─────────────────────────────────────────────────

CAUTION: Federal law prohibits transfer of this
prescription to any person other than the patient.

Signature: Dr. Michael Torres, MD`,
          structuredFields: [
            {
              key: "Prescriber",
              value: "Dr. Michael Torres, MD",
              confidence: 0.99,
            },
            {
              key: "Prescription Date",
              value: "January 30, 6",
              confidence: 0.99,
            },
            { key: "Patient Name", value: "Sarah Johnson", confidence: 0.98 },
            { key: "Patient DOB", value: "04/15/1985", confidence: 0.98 },
            {
              key: "Medication 1",
              value: "Ferrous Sulfate 325mg",
              confidence: 0.99,
            },
            {
              key: "Dosage 1",
              value: "1 tablet twice daily with food",
              confidence: 0.97,
            },
            { key: "Refills 1", value: "2", confidence: 0.98 },
            { key: "Medication 2", value: "Lisinopril 5mg", confidence: 0.99 },
            { key: "Dosage 2", value: "1 tablet once daily", confidence: 0.97 },
            { key: "Refills 2", value: "3", confidence: 0.98 },
          ],
          processingTime: 2.0,
        },
      },
    ],
  },

  // ── 3. Document Summarization ──────────────────────────────────────────────
  {
    id: "summarization",
    title: "Document Summarization",
    subtitle: "3 sample documents",
    icon: BookOpen,
    workflowType: "summarization",
    pipelineId: 1,
    additionalInstruction:
      "Produce a concise summary (maximum 5 sentences) based on the provided details. Generate the summary even if only minimal information is available",
    jsonSchema: null,
    documents: [
      {
        id: "business-report",
        type: "Business Report",
        name: "Business Report",
        icon: BarChart3,
        preview: "",
        result: {
          rawText: `QUARTERLY BUSINESS REPORT
TechStart LLC — Q4 2025

Prepared by:   Finance & Operations
Report Date:   January 30, 2026
Confidential — Internal Use Only

EXECUTIVE SUMMARY
Q4 2025 was a breakout quarter for TechStart LLC. Revenue reached $4.2M, up 34% year-over-year, driven by strong enterprise customer acquisition and expansion of our SaaS subscription tier. Operating costs were held to 61% of revenue, yielding an operating margin of 39% — the highest in company history.

FINANCIAL HIGHLIGHTS
Revenue:                          $4,200,000
  ├─ SaaS Subscriptions (68%):    $2,856,000
  ├─ Professional Services (22%):   $924,000
  └─ Other / One-time (10%):        $420,000

Operating Expenses:               $2,562,000
  ├─ Payroll & Benefits:           $1,680,000
  ├─ Infrastructure & Hosting:       $432,000
  └─ G&A:                            $450,000

EBITDA:                           $1,638,000  (39% margin)
Net Income:                       $1,104,000  (26.3% net margin)

CUSTOMER METRICS
Total Customers:                  412 (+28% YoY)
Net Revenue Retention:            118%
Churn Rate:                       2.1% (annual)
New Logos (Q4):                   47

OUTLOOK — Q1 2026
Pipeline coverage: 2.8×  |  Forecast Revenue: $4.8–5.1M`,
          structuredFields: [
            { key: "Company", value: "TechStart LLC", confidence: 0.99 },
            { key: "Period", value: "Q4 2025", confidence: 0.99 },
            {
              key: "Total Revenue",
              value: "$4,200,000 (+34% YoY)",
              confidence: 0.99,
            },
            {
              key: "SaaS Revenue",
              value: "$2,856,000 (68%)",
              confidence: 0.98,
            },
            {
              key: "Operating Expenses",
              value: "$2,562,000",
              confidence: 0.98,
            },
            {
              key: "EBITDA",
              value: "$1,638,000 (39% margin)",
              confidence: 0.99,
            },
            {
              key: "Net Income",
              value: "$1,104,000 (26.3%)",
              confidence: 0.99,
            },
            {
              key: "Total Customers",
              value: "412 (+28% YoY)",
              confidence: 0.97,
            },
            { key: "Net Revenue Retention", value: "118%", confidence: 0.98 },
            { key: "Q1 2026 Forecast", value: "$4.8–5.1M", confidence: 0.95 },
          ],
          processingTime: 2.6,
        },
      },
      {
        id: "legal-document",
        type: "Legal Document",
        name: "Legal Document",
        icon: Scale,
        preview: "",
        result: {
          rawText: `SERVICE AGREEMENT

This Service Agreement ("Agreement") is entered into as of January 30, 2026 ("Effective Date") by and between:

SERVICE PROVIDER:
  LEAP X Technologies Inc.
  1 Innovation Plaza, San Francisco, CA 94107
  ("Provider")

CLIENT:
  Momentum Ventures LLC
  345 Madison Avenue, New York, NY 10017
  ("Client")

1. SERVICES
   Provider agrees to deliver AI-powered document processing and OCR extraction services (the "Services") as detailed in Exhibit A, including API access, model fine-tuning on Client's document corpus, and 99.5% uptime SLA.

2. TERM
   This Agreement commences on the Effective Date and continues for twelve (12) months, automatically renewing for successive one-year terms unless terminated with 60 days' written notice.

3. FEES & PAYMENT
   Monthly Retainer:  $8,500 USD, invoiced on the 1st of each month
   Overage Rate:       $0.004 per API call beyond 500,000/month
   Payment Terms:      Net 15 days
   Late Fee:           1.5% per month

4. CONFIDENTIALITY
   Both parties agree to maintain strict confidentiality of all proprietary information disclosed during the term and for 3 years thereafter.

5. LIMITATION OF LIABILITY
   Provider's liability is limited to fees paid in the preceding 3-month period.

IN WITNESS WHEREOF, the parties have executed this Agreement.

LEAP X Technologies Inc.          Momentum Ventures LLC
By: _____________________         By: _____________________
Name: Alex Rivera, CEO            Name: Dana Park, COO
Date: January 30, 2026            Date: January 30, 2026`,
          structuredFields: [
            {
              key: "Agreement Type",
              value: "Service Agreement",
              confidence: 0.99,
            },
            {
              key: "Effective Date",
              value: "January 30, 2026",
              confidence: 0.99,
            },
            {
              key: "Provider",
              value: "LEAP X Technologies Inc.",
              confidence: 0.99,
            },
            { key: "Client", value: "Momentum Ventures LLC", confidence: 0.98 },
            {
              key: "Term",
              value: "12 months, auto-renewing",
              confidence: 0.97,
            },
            { key: "Monthly Retainer", value: "$8,500 USD", confidence: 0.99 },
            {
              key: "Overage Rate",
              value: "$0.004/API call over 500K/month",
              confidence: 0.98,
            },
            { key: "Payment Terms", value: "Net 15 days", confidence: 0.97 },
            { key: "Uptime SLA", value: "99.5%", confidence: 0.98 },
            {
              key: "Confidentiality Period",
              value: "3 years post-term",
              confidence: 0.96,
            },
          ],
          processingTime: 2.9,
        },
      },
    ],
  },
];
