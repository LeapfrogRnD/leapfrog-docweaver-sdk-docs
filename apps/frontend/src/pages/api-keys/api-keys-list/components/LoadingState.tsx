export function LoadingState() {
  return (
    <div className="bg-white border border-[rgba(0,0,0,0.1)] rounded-[14px] p-12 text-center">
      <div className="w-16 h-16 bg-[#f3f4f6] rounded-full flex items-center justify-center mx-auto mb-4">
        <div className="w-8 h-8 border-4 border-[#038e43] border-t-transparent rounded-full animate-spin"></div>
      </div>
      <p className="text-sm text-[#6b7280]">Loading API keys...</p>
    </div>
  );
}
