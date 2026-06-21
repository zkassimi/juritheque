export default function RTLWrapper({ children, className = '' }) {
  return (
    <div dir="rtl" lang="ar" className={`font-arabic text-right ${className}`}>
      {children}
    </div>
  )
}
