import HeroSection from '@/components/landing/HeroSection'
import MarketSummary from '@/components/landing/MarketSummary'
import FeatureShowcase from '@/components/landing/FeatureShowcase'
import StatisticsSection from '@/components/landing/StatisticsSection'
import Footer from '@/components/landing/Footer'

export default function HomePage() {
  return (
    <div className="min-h-screen">
      <HeroSection />
      <MarketSummary />
      <FeatureShowcase />
      <StatisticsSection />
      <Footer />
    </div>
  )
}
