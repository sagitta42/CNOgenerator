#!/bin/bash
BASE="../../../build_separate_noOMP"
EXEC="${BASE}/examples/spectralfit/src/spectralfitter"

$EXEC Sen_0.root hz_cno_1/TFC_sub/Hsub_cno_hz_1_0_npmts_dt1 sensitivity_dt1.cfg spl_cno_free.icc 2>&1 | tee sen_hz_cno_1_cno_free.log



