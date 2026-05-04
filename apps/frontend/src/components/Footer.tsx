import { PROJECT_NAME } from '@/constants/project.constants';

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-white border-t border-primary-ivory mt-auto">
      <div className="px-8 py-6">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-sm text-[#666]">
            © {currentYear} {PROJECT_NAME}. All rights reserved.
          </p>
          <div className="flex gap-6">
            <a href="#" className="text-sm text-[#666] hover:text-primary-brand transition-colors">
              Privacy Policy
            </a>
            <a href="#" className="text-sm text-[#666] hover:text-primary-brand transition-colors">
              Terms of Service
            </a>
            <a href="#" className="text-sm text-[#666] hover:text-primary-brand transition-colors">
              Support
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
