
% ------------------------------------------------------------------------------

% Increase counter:

if (exist('idx', 'var'));
  idx = idx + 1;
else;
  idx = 1;
end;

% Version, title and date:

VERSION                   (idx, [1: 14])  = 'Serpent 2.2.1' ;
COMPILE_DATE              (idx, [1: 20])  = 'Jan  1 2024 00:00:00' ;
DEBUG                     (idx, 1)        = 0 ;
TITLE                     (idx, [1:  8])  = 'Untitled' ;
INPUT_FILE_NAME           (idx, [1: 17])  = 'Sphere_1001_H-1.i' ;
