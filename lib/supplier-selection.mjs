/** Compare all selected matches, including other pages, but never hidden filter results. */
export function comparisonIds(selected, matchingRows) {
  const matching = new Set(matchingRows.map(row => row.supplierID));
  return [...new Set(selected)].filter(id => matching.has(id)).slice(0, 20);
}
