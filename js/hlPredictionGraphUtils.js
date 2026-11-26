/* hlPredictionGraphUtils.js — återskapad 2026-11-25.
   Originalfilen saknades i paketet. Den här versionen innehåller:
   1. HL_MATH: Hedlund-Leijon-principens matematik enligt författarens definitionsdokument (Drive).
   2. hlGraphUtils: beräkning av prognosträffsäkerhet. Den räknar ENBART på validerade utfall i
      HL_PAST_ELECTION_RESULTS. Inga utfall har hittats på eller återskapats; listan är tom tills
      validerade utfall (t.ex. V-Dem v17, väntas mars 2027) läggs in.
*/
(function () {
  'use strict';
  var H = 1.724, H_CI = [1.53, 1.96];
  window.HL_MATH = {
    source: 'Mathematical Definition of the Hedlund-Leijon Principle and the CDRS Model (author\'s Drive)',
    H: H, H_CI: H_CI, kappa: H / 8,
    cdrs: function (F, C, O, N, R, w) {
      var x = [F, C, O, N, R], ww = w || [0.2, 0.2, 0.2, 0.2, 0.2], s = 0, sw = 0;
      for (var i = 0; i < 5; i++) { s += ww[i] * x[i]; sw += ww[i]; }
      return s / sw;
    },
    normalize: function (z, min, max, higherIsStress) {
      if (max === min) return null;
      var x = Math.max(0, Math.min(1, (z - min) / (max - min)));
      return higherIsStress === false ? 1 - x : x;
    },
    // κ gäller demokratinivån (D ≤ κ). På CDRS-skalan motsvarar den 1 − κ = 0,7845 under antagandet
    // CDRS ≈ 1 − D (hl_calc.html, S3). Accelerationstermen och den logistiska risken från K1 har tagits bort,
    // eftersom de lägger κ på CDRS-skalan (S5) och α inte är skattad. Varning: CDRS ≥ 0,26 (kalibrerad 1996–2009, A3).
    kappaOnCDRS: 1 - H / 8,
    warnCDRS: 0.26,
    // Empirisk ledtidsgräns på CDRS-skalan (kalibrerad 1996–2009; hl_calc.html A6, S18). Inte κ.
    leadTimeCDRS: 0.21,
    // Riskband (hl_calc.html D8): 3-årsrisk 1/2/5/10/20 % för demokratier.
    bands: [0.13, 0.19, 0.26, 0.33, 0.39],
    estimateH: function (recoveries, erosions) {
      var m = function (a) { return a.reduce(function (x, y) { return x + y; }, 0) / a.length; };
      return (recoveries.length && erosions.length) ? m(recoveries) / m(erosions) : null;
    }
  };

  // Validerade historiska utfall. Format per rad (används av dashboardens valvy):
  // {country, date, type, fieldshiftPrediction, actualOutcome, fsPredictionScore, pollInstitutionsScore,
  //  userSubmittedScore, actualValidatedScore, sourceQuality, sourceRefs:[], sourceUrls:[]}
  window.HL_PAST_ELECTION_RESULTS = window.HL_PAST_ELECTION_RESULTS || [];
  window.HL_RESULTS_FEED_UPDATED_AT = window.HL_RESULTS_FEED_UPDATED_AT || '';

  var KEY = 'hlAccuracy_v2';
  function computeAccuracy() {
    var rows = (window.HL_PAST_ELECTION_RESULTS || []).filter(function (r) {
      return isFinite(r.actualValidatedScore) && isFinite(r.fsPredictionScore);
    });
    var outcomes = rows.map(function (r) {
      var fsErr = Math.abs(r.fsPredictionScore - r.actualValidatedScore);
      var pollErr = isFinite(r.pollInstitutionsScore) ? Math.abs(r.pollInstitutionsScore - r.actualValidatedScore) : null;
      var userErr = isFinite(r.userSubmittedScore) ? Math.abs(r.userSubmittedScore - r.actualValidatedScore) : null;
      var best = [['FieldShift', fsErr], ['Poll institutions', pollErr], ['Users', userErr]]
        .filter(function (x) { return x[1] != null; }).sort(function (a, b) { return a[1] - b[1]; })[0];
      return Object.assign({}, r, { analysis: {
        fsErr: fsErr, pollErr: pollErr, userErr: userErr, calibratedFs: r.fsPredictionScore,
        fsHitRaw: fsErr <= 0.05, winner: best ? best[0] : 'n/a', userSubmissionCount: 0, userSource: 'none',
        reason: 'Validated outcome vs. pre-election score (tolerance 0.05).' } });
    });
    var hits = outcomes.filter(function (o) { return o.analysis.fsHitRaw; }).length;
    var pct = outcomes.length ? 100 * hits / outcomes.length : null;
    return {
      outcomes: outcomes, rows: outcomes.length,
      accuracyPctRaw: pct, accuracyPctCalibrated: pct,
      formulaRaw: 'share of validated elections with |FS − validated| ≤ 0.05',
      formulaCalibrated: 'same (no calibration until n ≥ 10)',
      calibration: null, updatedAtText: new Date().toISOString().slice(0, 10)
    };
  }
  function persistAccuracy(stats) { try { localStorage.setItem(KEY, JSON.stringify(stats)); } catch (e) {} return stats; }
  function loadAccuracy() { try { return JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (e) { return null; } }
  window.hlGraphUtils = { computeAccuracy: computeAccuracy, persistAccuracy: persistAccuracy, loadAccuracy: loadAccuracy };
})();
