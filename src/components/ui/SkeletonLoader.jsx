export function SkeletonCard() {
  return (
    <div className="bg-white rounded-xl border border-gray-100 p-5 space-y-3 border-l-4 border-l-gray-200">
      <div className="flex gap-2">
        <div className="skeleton h-5 w-16 rounded" />
        <div className="skeleton h-5 w-12 rounded" />
      </div>
      <div className="skeleton h-5 w-3/4 rounded" />
      <div className="skeleton h-4 w-full rounded" />
      <div className="skeleton h-4 w-5/6 rounded" />
      <div className="flex gap-2 pt-1">
        <div className="skeleton h-4 w-14 rounded" />
        <div className="skeleton h-4 w-14 rounded" />
        <div className="skeleton h-4 w-14 rounded" />
      </div>
    </div>
  )
}

export function SkeletonText({ lines = 4 }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="skeleton h-4 rounded"
          style={{ width: i === lines - 1 ? '60%' : '100%' }}
        />
      ))}
    </div>
  )
}

export function SkeletonGrid({ count = 6 }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  )
}
