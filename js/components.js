// Shared Components - Navigation & Footer
// Run immediately (script is loaded at bottom of body, before Alpine.js deferred init)
(function() {
  injectNav();
  injectFooter();
})();

function injectNav() {
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';

  const navLinks = [
    { href: 'index.html', label: 'Home' },
    { href: 'research.html', label: 'Research' },
    { href: 'publications.html', label: 'Publications' },
    { href: 'tools.html', label: 'Tools' },
    { href: 'people.html', label: 'People' },
    { href: 'positions.html', label: 'Positions' },
    { href: 'collaborators.html', label: 'Collaborators' }
  ];

  const navHTML = `
  <nav x-data="{ open: false }" class="fixed top-0 left-0 right-0 z-50 bg-surface-dark/90 backdrop-blur-lg border-b border-white/10">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <a href="index.html" class="flex items-center gap-2 group">
          <svg class="w-8 h-8 text-primary-400 group-hover:text-primary-300 transition-colors" viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M16 2 C12 8, 12 12, 16 16 C20 12, 20 8, 16 2Z" fill="currentColor" opacity="0.3"/>
            <path d="M16 16 C12 20, 12 24, 16 30 C20 24, 20 20, 16 16Z" fill="currentColor" opacity="0.3"/>
            <path d="M8 6 Q16 16, 8 26" stroke-linecap="round"/>
            <path d="M24 6 Q16 16, 24 26" stroke-linecap="round"/>
            <circle cx="11" cy="10" r="1.5" fill="currentColor"/>
            <circle cx="21" cy="14" r="1.5" fill="currentColor"/>
            <circle cx="11" cy="18" r="1.5" fill="currentColor"/>
            <circle cx="21" cy="22" r="1.5" fill="currentColor"/>
          </svg>
          <div>
            <span class="text-white font-semibold text-lg tracking-tight">Hur Lab</span>
            <span class="hidden sm:inline text-primary-400/70 text-xs ml-2 font-mono">@UND</span>
          </div>
        </a>

        <!-- Desktop Nav -->
        <div class="hidden md:flex items-center gap-1">
          ${navLinks.map(link => `
            <a href="${link.href}"
               class="px-3 py-2 text-sm font-medium rounded-md transition-all duration-200 ${
                 currentPage === link.href
                   ? 'text-primary-400 bg-primary-400/10'
                   : 'text-gray-300 hover:text-white hover:bg-white/5'
               }">
              ${link.label}
            </a>
          `).join('')}
        </div>

        <!-- Right side -->
        <div class="flex items-center gap-3">
          <a href="https://github.com/hurlab" target="_blank" rel="noopener"
             class="text-gray-400 hover:text-white transition-colors p-2" title="GitHub">
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
          </a>
          <!-- Mobile menu button -->
          <button @click="open = !open" class="md:hidden text-gray-400 hover:text-white p-2">
            <svg x-show="!open" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
            <svg x-show="open" x-cloak class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile menu -->
    <div x-show="open" x-cloak x-transition:enter="transition ease-out duration-200"
         x-transition:enter-start="opacity-0 -translate-y-1" x-transition:enter-end="opacity-100 translate-y-0"
         x-transition:leave="transition ease-in duration-150"
         x-transition:leave-start="opacity-100 translate-y-0" x-transition:leave-end="opacity-0 -translate-y-1"
         class="md:hidden border-t border-white/10 bg-surface-dark/95 backdrop-blur-lg">
      <div class="px-4 py-3 space-y-1">
        ${navLinks.map(link => `
          <a href="${link.href}"
             class="block px-3 py-2 rounded-md text-base font-medium ${
               currentPage === link.href
                 ? 'text-primary-400 bg-primary-400/10'
                 : 'text-gray-300 hover:text-white hover:bg-white/5'
             }">
            ${link.label}
          </a>
        `).join('')}
      </div>
    </div>
  </nav>
  <!-- Spacer for fixed nav -->
  <div class="h-16"></div>
  `;

  document.body.insertAdjacentHTML('afterbegin', navHTML);
}

function injectFooter() {
  const footerHTML = `
  <footer class="bg-surface-dark text-gray-400 mt-20">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <!-- Contact -->
        <div>
          <h3 class="text-white font-semibold text-lg mb-4">Contact</h3>
          <div class="space-y-2 text-sm">
            <p class="flex items-start gap-2">
              <svg class="w-4 h-4 mt-0.5 text-primary-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
              1301 N Columbia Rd Stop 9037<br>Grand Forks, ND 58202-9037
            </p>
            <p class="flex items-center gap-2">
              <svg class="w-4 h-4 text-primary-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
              junguk.hur@med.UND.edu
            </p>
            <p class="flex items-center gap-2">
              <svg class="w-4 h-4 text-primary-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/></svg>
              (701) 777-6814
            </p>
          </div>
        </div>

        <!-- Quick Links -->
        <div>
          <h3 class="text-white font-semibold text-lg mb-4">Quick Links</h3>
          <ul class="space-y-2 text-sm">
            <li><a href="research.html" class="hover:text-primary-400 transition-colors">Research</a></li>
            <li><a href="publications.html" class="hover:text-primary-400 transition-colors">Publications</a></li>
            <li><a href="tools.html" class="hover:text-primary-400 transition-colors">Tools & Software</a></li>
            <li><a href="positions.html" class="hover:text-primary-400 transition-colors">Open Positions</a></li>
            <li><a href="https://github.com/hurlab" target="_blank" class="hover:text-primary-400 transition-colors">GitHub</a></li>
          </ul>
        </div>

        <!-- Affiliations -->
        <div>
          <h3 class="text-white font-semibold text-lg mb-4">Affiliations</h3>
          <ul class="space-y-2 text-sm">
            <li><a href="https://med.und.edu/biomedical-sciences/" target="_blank" class="hover:text-primary-400 transition-colors">Dept. of Biomedical Sciences</a></li>
            <li><a href="https://med.und.edu/" target="_blank" class="hover:text-primary-400 transition-colors">UND School of Medicine & Health Sciences</a></li>
            <li><a href="https://und.edu/" target="_blank" class="hover:text-primary-400 transition-colors">University of North Dakota</a></li>
          </ul>
          <div class="mt-4 flex items-center gap-3">
            <a href="https://orcid.org/0000-0002-0736-2149" target="_blank" class="text-xs bg-white/10 px-2 py-1 rounded hover:bg-white/20 transition-colors">
              ORCID
            </a>
            <a href="https://www.researchgate.net/profile/Junguk_Hur" target="_blank" class="text-xs bg-white/10 px-2 py-1 rounded hover:bg-white/20 transition-colors">
              ResearchGate
            </a>
          </div>
        </div>
      </div>

      <div class="border-t border-white/10 mt-8 pt-8 flex flex-col sm:flex-row justify-between items-center gap-4 text-xs text-gray-500">
        <p>&copy; ${new Date().getFullYear()} Hur Lab, University of North Dakota. All rights reserved.</p>
        <p>Dept. of Biomedical Sciences, School of Medicine & Health Sciences · <a href="http://hurlab.med.und.edu:8180/" class="hover:text-primary-400 transition-colors">Admin</a></p>
      </div>
    </div>
  </footer>
  `;

  document.body.insertAdjacentHTML('beforeend', footerHTML);
}
