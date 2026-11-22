import { PROJECT_OWNER, SOURCE_URL } from '../../app/projectIdentity';

export function ProjectCredits() {
  return (
    <div className="space-y-2 text-sm leading-relaxed">
      <p><strong>StructLib</strong> · Created by {PROJECT_OWNER} with open-source contributors.</p>
      <ul className="flex flex-wrap gap-x-4 gap-y-1" aria-label="Project credits">
        <li><a className="underline underline-offset-4" href={SOURCE_URL}>Source on GitHub</a></li>
        <li><a className="underline underline-offset-4" href={`${SOURCE_URL}/blob/main/LICENSE`}>MIT License</a></li>
        <li><a className="underline underline-offset-4" href={`${import.meta.env.BASE_URL}CREDITS.txt`}>Source credits</a></li>
        <li><a className="underline underline-offset-4" href={`${SOURCE_URL}/blob/main/LICENSE_ENGINEERING.md`}>Engineering-use notice</a></li>
      </ul>
    </div>
  );
}
