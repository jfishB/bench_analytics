import { X } from "lucide-react";
import { Button } from "./button";

interface AlgorithmModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function AlgorithmModal({ isOpen, onClose }: AlgorithmModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
      <div
        className="relative w-full max-w-3xl max-h-[90vh] bg-white rounded-2xl shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-semibold text-gray-900">
            Our Algorithm
          </h2>
          <button
            onClick={onClose}
            className="p-2 rounded-full hover:bg-gray-100 transition-colors"
            aria-label="Close"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="overflow-y-auto max-h-[calc(90vh-80px)] px-6 py-6">
          <div className="space-y-6">
            {/* Introduction */}
            <section>
              <p className="text-gray-600 leading-relaxed">
                Modern baseball strategy, heavily influenced by sabermetrics,
                dictates placing the best hitters at the top of the lineup to
                maximize their plate appearances. Our algorithm uses advanced
                statistics to optimize your batting order for maximum run
                production.
              </p>
            </section>

            {/* Key Principle */}
            <section className="bg-blue-50 rounded-xl p-4 border border-blue-100">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Core Principle
              </h3>
              <p className="text-gray-700 text-sm leading-relaxed">
                Focus on getting high On-Base Percentage (OBP) players on base
                early to set up high Slugging Percentage (SLG) players for power
                opportunities in the middle of the lineup.
              </p>
            </section>

            {/* Algorithm Breakdown */}
            <section>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Lineup Optimization Strategy
              </h3>

              <div className="space-y-4">
                {/* Top of Order */}
                <div className="border-l-4 border-primary pl-4">
                  <h4 className="font-semibold text-gray-900 mb-2">
                    Slots 1, 2, and 4: Your Best Hitters
                  </h4>
                  <div className="space-y-3 text-sm">
                    <div>
                      <span className="font-medium text-primary">
                        #1 Leadoff:
                      </span>
                      <span className="text-gray-700 ml-2">
                        Highest OBP player - getting on base is paramount for
                        starting innings
                      </span>
                    </div>
                    <div>
                      <span className="font-medium text-primary">
                        #2 Second:
                      </span>
                      <span className="text-gray-700 ml-2">
                        Best overall hitter (highest wOBA/OPS) - drives in the
                        leadoff runner or sets the table
                      </span>
                    </div>
                    <div>
                      <span className="font-medium text-primary">
                        #4 Cleanup:
                      </span>
                      <span className="text-gray-700 ml-2">
                        Primary power hitter (highest SLG) - positioned to
                        "clean the bases"
                      </span>
                    </div>
                  </div>
                </div>

                {/* Middle Order */}
                <div className="border-l-4 border-secondary pl-4">
                  <h4 className="font-semibold text-gray-900 mb-2">
                    Slots 3 and 5: Supporting Cast
                  </h4>
                  <div className="space-y-3 text-sm">
                    <div>
                      <span className="font-medium text-secondary-foreground">
                        #3 Third:
                      </span>
                      <span className="text-gray-700 ml-2">
                        Strong all-around hitter - bridge to the cleanup spot
                      </span>
                    </div>
                    <div>
                      <span className="font-medium text-secondary-foreground">
                        #5 Fifth:
                      </span>
                      <span className="text-gray-700 ml-2">
                        Secondary power hitter - provides "lineup protection"
                      </span>
                    </div>
                  </div>
                </div>

                {/* Bottom Order */}
                <div className="border-l-4 border-muted pl-4">
                  <h4 className="font-semibold text-gray-900 mb-2">
                    Slots 6-9: Descending Quality
                  </h4>
                  <p className="text-sm text-gray-700">
                    Arranged in descending order by OPS/wOBA. The player with
                    the best OBP in this group often bats 6th as a "second
                    leadoff hitter."
                  </p>
                </div>
              </div>
            </section>

            {/* Key Statistics */}
            <section>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Key Statistics We Use
              </h3>
              <div className="grid gap-3">
                <div className="bg-gray-50 rounded-lg p-3">
                  <h5 className="font-semibold text-sm text-gray-900">
                    wOBA (Weighted On-Base Average)
                  </h5>
                  <p className="text-xs text-gray-600 mt-1">
                    Reflects overall offensive value by weighting different ways
                    of reaching base
                  </p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <h5 className="font-semibold text-sm text-gray-900">
                    OBP (On-Base Percentage)
                  </h5>
                  <p className="text-xs text-gray-600 mt-1">
                    Percentage of times a player reaches base via hit, walk, or
                    HBP
                  </p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <h5 className="font-semibold text-sm text-gray-900">
                    SLG (Slugging Percentage)
                  </h5>
                  <p className="text-xs text-gray-600 mt-1">
                    Measures power by calculating total bases per at-bat
                  </p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <h5 className="font-semibold text-sm text-gray-900">
                    OPS (On-Base Plus Slugging)
                  </h5>
                  <p className="text-xs text-gray-600 mt-1">
                    Combines ability to get on base with power hitting (OBP +
                    SLG)
                  </p>
                </div>
              </div>
            </section>

            {/* Additional Strategies */}
            <section className="bg-gray-50 rounded-xl p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Additional Considerations
              </h3>
              <ul className="space-y-2 text-sm text-gray-700">
                <li className="flex items-start">
                  <span className="text-primary mr-2">•</span>
                  <span>
                    <strong>Handedness:</strong> Alternate left- and
                    right-handed batters to prevent favorable pitcher matchups
                  </span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary mr-2">•</span>
                  <span>
                    <strong>Speed Placement:</strong> Position faster players in
                    front of high-contact hitters
                  </span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary mr-2">•</span>
                  <span>
                    <strong>Matchup Adjustments:</strong> Different lineups for
                    RHP vs LHP based on splits
                  </span>
                </li>
              </ul>
            </section>

            {/* Expected Impact */}
            <section className="bg-primary/5 rounded-xl p-4 border border-primary/20">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Expected Impact
              </h3>
              <p className="text-sm text-gray-700 leading-relaxed">
                By applying these sabermetric principles, a manager can
                theoretically gain an estimated{" "}
                <strong className="text-primary">5 to 15 runs</strong> over a
                full season, which can translate to{" "}
                <strong className="text-primary">1 to 3 additional wins</strong>
                .
              </p>
            </section>
          </div>
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-white border-t border-gray-200 px-6 py-4">
          <Button onClick={onClose} className="w-full" size="lg">
            Got it
          </Button>
        </div>
      </div>
    </div>
  );
}
