// Code generated by "stringer -type=MatchType"; DO NOT EDIT.

package dissect

import "strconv"

func _() {
	// An "invalid array index" compiler error signifies that the constant values have changed.
	// Re-run the stringer command to generate them again.
	var x [1]struct{}
	_ = x[QuickMatch-1]
	_ = x[Ranked-2]
	_ = x[CustomGameLocal-3]
	_ = x[CustomGameOnline-4]
	_ = x[Standard-8]
}

const (
	_MatchType_name_0 = "QuickMatchRankedCustomGameLocalCustomGameOnline"
	_MatchType_name_1 = "Standard"
)

var (
	_MatchType_index_0 = [...]uint8{0, 10, 16, 31, 47}
)

func (i MatchType) String() string {
	switch {
	case 1 <= i && i <= 4:
		i -= 1
		return _MatchType_name_0[_MatchType_index_0[i]:_MatchType_index_0[i+1]]
	case i == 8:
		return _MatchType_name_1
	default:
		return "MatchType(" + strconv.FormatInt(int64(i), 10) + ")"
	}
}
