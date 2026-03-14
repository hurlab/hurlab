// Publications - PubMed API Integration
const PUB_CONFIG = {
  searchUrl: 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi',
  summaryUrl: 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi',
  authorQuery: '"Hur, Junguk"[FAU] OR "Hur, Jung Uk"[FAU]',
  piName: 'Hur J',
  retmax: 200,
  cacheKey: 'hurlab_pubmed_cache',
  cacheDuration: 24 * 60 * 60 * 1000 // 24 hours
};

async function fetchPubMedIds() {
  const cached = getCache();
  if (cached) return cached;

  try {
    const searchParams = new URLSearchParams({
      db: 'pubmed',
      term: PUB_CONFIG.authorQuery,
      retmode: 'json',
      retmax: PUB_CONFIG.retmax,
      sort: 'date'
    });

    const searchRes = await fetch(`${PUB_CONFIG.searchUrl}?${searchParams}`);
    const searchData = await searchRes.json();
    const ids = searchData.esearchresult.idlist;

    if (!ids || ids.length === 0) return null;

    // Fetch summaries in batches of 50
    const allSummaries = [];
    for (let i = 0; i < ids.length; i += 50) {
      const batch = ids.slice(i, i + 50);
      const summaryParams = new URLSearchParams({
        db: 'pubmed',
        id: batch.join(','),
        retmode: 'json'
      });

      const summaryRes = await fetch(`${PUB_CONFIG.summaryUrl}?${summaryParams}`);
      const summaryData = await summaryRes.json();

      for (const id of batch) {
        const article = summaryData.result[id];
        if (article) {
          allSummaries.push({
            pmid: id,
            title: article.title,
            authors: article.authors ? article.authors.map(a => a.name).join(', ') : '',
            journal: article.fulljournalname || article.source,
            year: article.pubdate ? article.pubdate.split(' ')[0] : '',
            volume: article.volume || '',
            issue: article.issue || '',
            pages: article.pages || '',
            doi: article.elocationid || '',
            pubdate: article.pubdate || ''
          });
        }
      }

      // Rate limiting: wait 350ms between batches
      if (i + 50 < ids.length) {
        await new Promise(resolve => setTimeout(resolve, 350));
      }
    }

    setCache(allSummaries);
    return allSummaries;
  } catch (error) {
    console.error('PubMed API error:', error);
    return null;
  }
}

function getCache() {
  try {
    const cached = sessionStorage.getItem(PUB_CONFIG.cacheKey);
    if (!cached) return null;
    const { data, timestamp } = JSON.parse(cached);
    if (Date.now() - timestamp > PUB_CONFIG.cacheDuration) return null;
    return data;
  } catch {
    return null;
  }
}

function setCache(data) {
  try {
    sessionStorage.setItem(PUB_CONFIG.cacheKey, JSON.stringify({
      data,
      timestamp: Date.now()
    }));
  } catch {
    // sessionStorage full or unavailable
  }
}

function highlightPI(authors) {
  return authors.replace(/(Hur\s*J\b)/gi, '<strong class="text-primary-700">$1</strong>');
}

function isRecent(year) {
  const currentYear = new Date().getFullYear();
  return parseInt(year) >= currentYear - 2;
}

// Export for Alpine.js use
window.PubMedAPI = { fetchPubMedIds, highlightPI, isRecent };
