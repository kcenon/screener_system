import { Link } from 'react-router-dom'
import { Github, Mail } from 'lucide-react'

export default function Footer() {
  const currentYear = new Date().getFullYear()

  const footerLinks = {
    platform: [
      { name: '기능', path: '/#features' },
      { name: '스크리너', path: '/screener' },
      { name: '시장 현황', path: '/market' },
      { name: '가격', path: '/#pricing' },
    ],
    resources: [
      { name: 'API 문서', path: '/docs/api' },
      { name: '사용 가이드', path: '/docs/guide' },
      { name: '자주 묻는 질문', path: '/docs/faq' },
      { name: '업데이트 노트', path: '/docs/updates' },
    ],
    company: [
      { name: '회사 소개', path: '/about' },
      { name: '블로그', path: '/blog' },
      { name: '채용', path: '/careers' },
      { name: '문의하기', path: '/contact' },
    ],
    legal: [
      { name: '이용약관', path: '/terms' },
      { name: '개인정보처리방침', path: '/privacy' },
      { name: '쿠키 정책', path: '/cookies' },
      { name: '면책 조항', path: '/disclaimer' },
    ],
  }

  return (
    <footer className="bg-gray-900 dark:bg-gray-950 text-gray-300 dark:text-gray-400 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 mb-8">
          {/* Brand Section */}
          <div className="lg:col-span-1">
            <div className="mb-4">
              <h3 className="text-2xl font-bold text-white">THE SCREENER</h3>
              <p className="text-sm text-gray-400 dark:text-gray-500 mt-1 transition-colors">스톡 스크리너</p>
            </div>
            <p className="text-sm text-gray-400 dark:text-gray-500 mb-4 transition-colors">
              한국 주식 시장의 데이터 기반 투자 분석 플랫폼
            </p>
            <div className="flex gap-4">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 dark:text-gray-500 hover:text-white dark:hover:text-gray-300 transition-colors"
                aria-label="GitHub"
              >
                <Github className="w-6 h-6" />
              </a>
              <a
                href="mailto:contact@example.com"
                className="text-gray-400 dark:text-gray-500 hover:text-white dark:hover:text-gray-300 transition-colors"
                aria-label="Email"
              >
                <Mail className="w-6 h-6" />
              </a>
            </div>
          </div>

          {/* Platform Links */}
          <div>
            <h4 className="text-white dark:text-gray-200 font-semibold mb-4 transition-colors">플랫폼</h4>
            <ul className="space-y-2">
              {footerLinks.platform.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.path}
                    className="text-sm hover:text-white dark:hover:text-gray-300 transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources Links */}
          <div>
            <h4 className="text-white dark:text-gray-200 font-semibold mb-4 transition-colors">리소스</h4>
            <ul className="space-y-2">
              {footerLinks.resources.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.path}
                    className="text-sm hover:text-white dark:hover:text-gray-300 transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Company Links */}
          <div>
            <h4 className="text-white dark:text-gray-200 font-semibold mb-4 transition-colors">회사</h4>
            <ul className="space-y-2">
              {footerLinks.company.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.path}
                    className="text-sm hover:text-white dark:hover:text-gray-300 transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal Links */}
          <div>
            <h4 className="text-white dark:text-gray-200 font-semibold mb-4 transition-colors">법적 고지</h4>
            <ul className="space-y-2">
              {footerLinks.legal.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.path}
                    className="text-sm hover:text-white dark:hover:text-gray-300 transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="border-t border-gray-800 dark:border-gray-900 pt-8 mb-8 transition-colors">
          <div className="bg-gray-800 dark:bg-gray-900 rounded-lg p-4 transition-colors">
            <p className="text-xs text-gray-400 dark:text-gray-500 leading-relaxed transition-colors">
              <strong className="text-gray-300 dark:text-gray-400 transition-colors">투자 유의사항:</strong> 본 플랫폼에서
              제공하는 정보는 투자 참고용이며, 투자 권유를 목적으로 하지 않습니다.
              모든 투자 결정은 투자자 본인의 책임 하에 이루어져야 하며, 투자로 인한
              손실에 대해서는 당사가 책임지지 않습니다. 과거 성과가 미래 수익을
              보장하지 않습니다.
            </p>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-800 dark:border-gray-900 pt-8 transition-colors">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-gray-400 dark:text-gray-500 transition-colors">
              © {currentYear} Stock Screening Platform. All rights reserved.
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-600 transition-colors">
              Built with React, TypeScript, and TailwindCSS
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}
