/**
 * 조건부 클래스 이름 결합 유틸리티
 *
 * @example
 * cn('btn', isActive && 'btn-active', size === 'lg' && 'btn-lg')
 * // => 'btn btn-active btn-lg' (조건이 true일 때)
 */
export function cn(...inputs: (string | false | null | undefined)[]): string {
  return inputs.filter(Boolean).join(' ');
}
