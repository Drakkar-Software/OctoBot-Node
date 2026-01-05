export function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="border-t py-4 px-6">
      <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
        <p className="text-muted-foreground text-sm">
          OctoBot Node - {currentYear}
        </p>
        <div className="flex items-center gap-4">
        </div>
      </div>
    </footer>
  )
}
