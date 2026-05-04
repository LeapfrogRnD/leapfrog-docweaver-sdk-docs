import { Alert, AlertTitle, AlertDescription } from '../../../../components/ui/Alert';

export function SecurityAlert() {
  return (
    <Alert variant="success" className="rounded-[10px] p-4">
      <AlertTitle>Keep your API keys secure</AlertTitle>
      <AlertDescription>
        API keys provide access to your OCR system. Never share them in publicly accessible areas
        such as GitHub, client-side code, or unsecured channels.
      </AlertDescription>
    </Alert>
  );
}
