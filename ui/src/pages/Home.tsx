import { useState } from 'react'
import { cn } from '@/lib/utils'
import { Phase } from '@/models/Phase'
import { Separator } from '@/components/ui/separator'
import TranslationSection from '@/components/TranslationSection'
import ComparisonSection from '@/components/ComparisonSection'

const Home = () => {
  const [phase, setPhase] = useState(Phase.TRANSLATION)

  return (
    <section>
      {/* Phase Navigation */}
      <div className="flex gap-4 mb-6">
        <button
          className={`px-4 py-2 rounded-lg transition-colors ${
            phase === Phase.TRANSLATION
              ? 'bg-blue-500 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
          onClick={() => setPhase(Phase.TRANSLATION)}
        >
          Translation
        </button>
        <button
          className={`px-4 py-2 rounded-lg transition-colors ${
            phase === Phase.AI_COMPARISON
              ? 'bg-blue-500 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
          onClick={() => setPhase(Phase.AI_COMPARISON)}
        >
          AI Comparison
        </button>
      </div>

      <Separator className="mb-6" />

      {
        phase === Phase.TRANSLATION ?
          <TranslationSection />
          :
          <div id="comparison-section">
            <ComparisonSection />
          </div>
      }
    </section>
  )
}

export default Home
